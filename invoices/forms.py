from django import forms
from .models import InvoiceFile

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = InvoiceFile
        fields = ['file']
