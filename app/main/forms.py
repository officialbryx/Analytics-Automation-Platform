from django import forms
from .models import Requests

class RequestForm(forms.Form):
    report_name = forms.CharField(
        label="Report Name",
        help_text="Any title you like. It becomes the Excel file name.",
        error_messages={
            "required": 'Please insert a proper "Report Name".',
        },
    )
    information = forms.CharField(
        label="Notes (optional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    tickers = forms.MultipleChoiceField(
        choices=Requests.TICKER_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
        }),
        label="Companies",
        help_text="Pick one or more companies."
    )
    statement_type = forms.ChoiceField(
        label="Financial Statement",
        choices=Requests.STATEMENT_TYPE,
        initial="IS",
    )
    period_type = forms.ChoiceField(
        label="Report By",
        choices=Requests.PERIOD_TYPE,
        widget=forms.RadioSelect,
        initial="FY",
    )
    start_year = forms.IntegerField(
        label="From Fiscal Year",
        initial=2019,
        min_value=2009,
        max_value=2021,
    )
    end_year = forms.IntegerField(
        label="To Fiscal Year",
        initial=2020,
        min_value=2009,
        max_value=2021,
        help_text="SEC data is available for fiscal years 2009 to 2021 only."
    )

    placeholders = {
        "report_name": "e.g. Apple Income Statement 2019-2020",
        "information": "Anything you want to remember about this report",
        "tickers": "Select one or more companies",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            if field_name in ["period_type"]:
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