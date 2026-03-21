from django import forms

class ApiSettingsForm(forms.Form):
    google_ai_api_key = forms.CharField(
        label="Google AI API Key",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Google AI API Key'})
    ) 