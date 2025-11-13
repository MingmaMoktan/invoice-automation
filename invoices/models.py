from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

class InvoiceFile(models.Model):
    file = models.FileField(upload_to='invoices/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # raw OCR text
    extracted_text = models.TextField(blank=True, null=True)

    # parsed fields (simple strings for now)
    invoice_number = models.CharField(max_length=200, blank=True, null=True)
    invoice_date = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.file.name

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()  # rich text editor
    published_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title
    
# invoices/models.py
from django.db import models
from django.contrib.auth.models import User  # default Django User

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # link invoice to user
    number = models.CharField(max_length=50)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Invoice {self.number} - {self.user.username}"

