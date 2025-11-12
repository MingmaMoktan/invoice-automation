from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

class InvoiceFile(models.Model):
    file = models.FileField(upload_to='invoices/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.file.name

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()  # rich text editor
    published_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title