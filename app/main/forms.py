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
        label="Brief Information / Justification",
        widget=forms.Textarea(attrs={"rows": 3, "cols": 40}),
    )
    ticker = forms.CharField(
        label="Company Ticker(s)",
        help_text="e.g. AAPL, MSFT, GOOGL",
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
        "report_name": "Enter report title (e.g., Tech Peers Revenue Analysis)",
        "information": "Enter brief details or reason for this request",
        "ticker": "Enter stock ticker symbols separated by commas",
        "start_year": "e.g., 2020",
        "end_year": "e.g., 2025",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            if field_name in ["period_type", "display_unit"]:
                self.fields[field_name].widget.attrs.update({"class": "form-check"})
            else:
                self.fields[field_name].widget.attrs.update({"class": "form-control"})

        for field_name, placeholder in self.placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({"placeholder": placeholder})