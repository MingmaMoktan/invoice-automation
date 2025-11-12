from django.contrib import admin
from .models import InvoiceFile
from .models import BlogPost

@admin.register(InvoiceFile)
class InvoiceFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')
    readonly_fields = ('extracted_text',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'author')
