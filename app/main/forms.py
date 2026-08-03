from django import forms
from .models import Requests

class RequestForm(forms.ModelForm):
    # [EDIT HERE]
    # Custom placeholder text for the form fields. Default value is empty
    placeholders = {
        "request_name": "Request Title",
        "information": "Brief information of the request",
    }

    class Meta:
        model = Requests
        fields = (
            "request_name",
            "information",
        )

        # [EDIT HERE]
        # Custom labels for the form fields. Default value is the field name
        labels = {
            "request_name": "Request Name",
            "information": "Information",
        }

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        # Adds Bootstrap class to the form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs["class"] = "form-control"

        # Adds placeholder text to the form fields
        for field_name, placeholder_text in self.placeholders.items():
            self.fields[field_name].widget.attrs["placeholder"] = placeholder_text
