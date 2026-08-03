from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()

        if commit:
            user.save()
        return user