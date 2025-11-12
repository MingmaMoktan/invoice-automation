import os
import tempfile
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import InvoiceForm
from .models import InvoiceFile

from PIL import Image
import pytesseract
from pdf2image import convert_from_path

def landing(request):
    return render(request, 'invoices/landing.html')

def pricing(request):
    return render(request, 'invoices/pricing.html')

def about(request):
    return render(request, 'invoices/about.html')

def blog(request):
    return render(request, 'invoices/blog.html')

def contact(request):
    return render(request, 'invoices/contact.html')


# Helper: run tesseract on an image path and return text
def ocr_image_file(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        text = f"[OCR error] {e}"
    return text

def upload_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.save()  # save file to storage so .path is available

            file_path = invoice.file.path
            file_ext = os.path.splitext(file_path)[1].lower()

            extracted_text = ""

            if file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                extracted_text = ocr_image_file(file_path)
            elif file_ext in ['.pdf']:
                # convert PDF to images then OCR each page
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # convert_from_path returns list of PIL images
                        images = convert_from_path(file_path, dpi=300, output_folder=tmpdir)
                        page_texts = []
                        for i, img in enumerate(images):
                            # optionally save image to temp file then ocr
                            temp_img_path = os.path.join(tmpdir, f"page_{i}.png")
                            img.save(temp_img_path, 'PNG')
                            page_texts.append(ocr_image_file(temp_img_path))
                        extracted_text = "\n\n--- PAGE BREAK ---\n\n".join(page_texts)
                except Exception as e:
                    extracted_text = f"[PDF -> image conversion error] {e}"
            else:
                extracted_text = "[Unsupported file type]"

            invoice.extracted_text = extracted_text
            invoice.save()

            return render(request, 'invoices/result.html', {'invoice': invoice})
    else:
        form = InvoiceForm()
    return render(request, 'invoices/upload.html', {'form': form})

