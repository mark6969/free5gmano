from django import forms


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=150, required=True)
    password = forms.CharField(max_length=128, required=True)
    email = forms.EmailField(max_length=254, required=True)
