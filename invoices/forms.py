from django import forms
from .models import InvoiceFile

# Single invoice upload
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = InvoiceFile
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'accept': '.pdf,.png,.jpg,.jpeg,.tiff,.bmp'})
        }

# Multiple invoice upload
class MultiInvoiceForm(forms.Form):
    files = forms.FileField(
        label='Select invoices',
        required=True
    )
