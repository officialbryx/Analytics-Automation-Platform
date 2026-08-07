from django import forms
from .models import Requests

class RequestForm(forms.Form):
    report_name = forms.CharField(
        label="Report Name",
        error_messages={
            "required": 'Please insert a proper "Report Name".',
        },
    )
    information = forms.CharField(
        label="Brief Information",
        widget=forms.Textarea(attrs={"rows": 3, "cols": 40}),
    )
    tickers = forms.MultipleChoiceField(
        choices=Requests.TICKER_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
        }),
        help_text="Hold Ctrl (Cmd on Mac) to select multiple tickers."
    )
    statement_type = forms.ChoiceField(
        label="Financial Statement Type",
        choices=Requests.STATEMENT_TYPE,
        initial="IS",
    )
    period_type = forms.ChoiceField(
        label="Time Frequency",
        choices=Requests.PERIOD_TYPE,
        widget=forms.RadioSelect,
        initial="FY",
    )
    start_year = forms.IntegerField(
        label="Start Fiscal Year",
        initial=2020,
    )
    end_year = forms.IntegerField(
        label="End Fiscal Year",
        initial=2025,
    )
    display_unit = forms.ChoiceField(
        label="Display Numbers In",
        choices=Requests.DISPLAY_UNIT,
        widget=forms.RadioSelect,
        initial="1000000",
    )

    placeholders = {
        "report_name": "Enter report title (e.g., Balance Sheet Analysis for AAPL 2025)",
        "information": "Enter brief information for this request",
        "tickers": "Select one or more ticker symbols",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            if field_name in ["period_type", "display_unit"]:
                self.fields[field_name].widget.attrs.update({"class": "form-check-input"})
            elif field_name == "tickers":
                self.fields[field_name].widget.attrs.update({"class": "form-control select2"})
            else:
                self.fields[field_name].widget.attrs.update({"class": "form-control"})

        for field_name, placeholder in self.placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({"placeholder": placeholder})

    def clean_tickers(self):
        """Validate that at least one ticker is selected"""
        tickers = self.cleaned_data.get('tickers')
        if not tickers or len(tickers) == 0:
            raise forms.ValidationError("Please select at least one ticker symbol.")
        return tickers

    def clean(self):
        """Validate year range"""
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')
        
        if start_year and end_year:
            if start_year > end_year:
                raise forms.ValidationError("Start year cannot be greater than end year.")
            if end_year - start_year > 20:
                raise forms.ValidationError("Year range cannot exceed 20 years.")
        
        return cleaned_data