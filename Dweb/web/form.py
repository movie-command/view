from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.CharField()
    sex = forms.CharField()
    birthday=forms.CharField()
    password = forms.CharField()

class Recommand(forms.Form):
    ty = forms.CharField()
    tyear = forms.IntegerField()