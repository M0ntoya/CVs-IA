# cvchat/forms.py
from django import forms

class UploadCVForm(forms.Form):
    cv_file = forms.FileField(label='Sube tu CV en PDF')
