from django.contrib import admin
from .models import InvoiceFile

@admin.register(InvoiceFile)
class InvoiceFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')
    readonly_fields = ('extracted_text',)
