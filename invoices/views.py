import os
import re
import csv
import tempfile
from io import StringIO
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .forms import InvoiceForm, MultiInvoiceForm
from .models import InvoiceFile, BlogPost
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# ===== Static Pages =====
def landing(request):
    return render(request, 'invoices/landing.html')

def pricing(request):
    return render(request, 'invoices/pricing.html')

def about(request):
    return render(request, 'invoices/about.html')

def blog(request):
    posts = BlogPost.objects.all().order_by('-published_at')
    return render(request, 'invoices/blog.html', {'posts': posts})

def blog_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    return render(request, 'invoices/blog_detail.html', {'post': post})

def contact(request):
    return render(request, 'invoices/contact.html')


# ===== OCR Helper =====
def ocr_image_file(image_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        return f"[OCR error] {e}"


def parse_invoice_fields(text):
    """Parse invoice number, date, and total amount from OCR text."""
    invoice_no = invoice_date = total_amount = None
    if not text:
        return {'invoice_number': None, 'invoice_date': None, 'total_amount': None}

    txt = text.replace('\n', ' ').replace('\r', ' ')

    # Invoice number
    for pat in [
        r'Invoice\s*(?:No\.?|Number)?[:\s#-]*([A-Za-z0-9\-_/]+)',
        r'Inv(?:ice)?\s*#[:\s]*([A-Za-z0-9\-_/]+)',
        r'Invoice\s*[:\s]*([A-Za-z0-9\-_/]+)'
    ]:
        if m := re.search(pat, txt, flags=re.IGNORECASE):
            invoice_no = m.group(1).strip()
            break

    # Date
    for pat in [
        r'(\d{1,2}\s+(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\s+\d{4})',
        r'(\d{1,2}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{2,4})',
        r'(\d{4}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{1,2})'
    ]:
        if m := re.search(pat, txt, flags=re.IGNORECASE):
            invoice_date = m.group(1).strip()
            break

    # Total amount
    for pat in [
        r'(?:Total\s*Due|Amount\s*Due|Balance\s*Due|TOTAL|Total)[:\s]*\$?([\d,]+\.\d{2})',
        r'(?:Total|TOTAL|Amount)[:\s]*\$?([\d,]+\.\d{2})'
    ]:
        if m := re.search(pat, txt, flags=re.IGNORECASE):
            total_amount = m.group(1).strip()
            break

    if not total_amount:
        all_money = re.findall(r'\$?([\d,]+\.\d{2})', txt)
        if all_money:
            total_amount = all_money[-1]

    return {'invoice_number': invoice_no, 'invoice_date': invoice_date, 'total_amount': total_amount}


# ===== Single Invoice Upload =====
def upload_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.save()

            file_path = invoice.file.path
            file_ext = os.path.splitext(file_path)[1].lower()
            extracted_text = ""

            if file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                extracted_text = ocr_image_file(file_path)
            elif file_ext == '.pdf':
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        images = convert_from_path(file_path, dpi=300, output_folder=tmpdir)
                        pages_text = []
                        for i, img in enumerate(images):
                            temp_img = os.path.join(tmpdir, f"page_{i}.png")
                            img.save(temp_img, 'PNG')
                            pages_text.append(ocr_image_file(temp_img))
                        extracted_text = "\n\n--- PAGE BREAK ---\n\n".join(pages_text)
                except Exception as e:
                    extracted_text = f"[PDF conversion error] {e}"
            else:
                extracted_text = "[Unsupported file type]"

            invoice.extracted_text = extracted_text
            invoice.save()

            return render(request, 'invoices/result.html', {'invoice': invoice})
    else:
        form = InvoiceForm()
    return render(request, 'invoices/upload.html', {'form': form})


# ===== Bulk Invoice Upload =====
def upload_invoices(request):
    """Multiple invoice upload with CSV generation."""
    results = []

    if request.method == 'POST':
        form = MultiInvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')  # This will now correctly get all uploaded files
            for file in files:
                invoice = InvoiceFile.objects.create(file=file)
                file_path = invoice.file.path
                file_ext = os.path.splitext(file_path)[1].lower()
                extracted_text = ""

                if file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                    extracted_text = ocr_image_file(file_path)
                elif file_ext == '.pdf':
                    try:
                        with tempfile.TemporaryDirectory() as tmpdir:
                            images = convert_from_path(file_path, dpi=300, output_folder=tmpdir)
                            pages_text = []
                            for i, img in enumerate(images):
                                temp_img = os.path.join(tmpdir, f"page_{i}.png")
                                img.save(temp_img, 'PNG')
                                pages_text.append(ocr_image_file(temp_img))
                            extracted_text = "\n\n--- PAGE BREAK ---\n\n".join(pages_text)
                    except Exception as e:
                        extracted_text = f"[PDF conversion error] {e}"

                invoice.extracted_text = extracted_text
                invoice.save()

                parsed = parse_invoice_fields(extracted_text)
                results.append({
                    'filename': file.name,
                    'invoice_number': parsed['invoice_number'],
                    'invoice_date': parsed['invoice_date'],
                    'total_amount': parsed['total_amount']
                })

            # Save CSV in memory
            csv_buffer = StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=['filename', 'invoice_number', 'invoice_date', 'total_amount'])
            writer.writeheader()
            writer.writerows(results)
            request.session['invoice_csv'] = csv_buffer.getvalue()

            return render(request, 'invoices/result_bulk.html', {'results': results})

    else:
        form = MultiInvoiceForm()

    return render(request, 'invoices/bulk_upload.html', {'form': form})


# ===== CSV Download =====
def download_invoices_csv(request):
    csv_data = request.session.get('invoice_csv', '')
    if not csv_data:
        return HttpResponse("No data to download.", content_type="text/plain")

    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="invoices_extracted.csv"'
    return response


from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('landing')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Invoice  # assuming you have an Invoice model
import os
from django.conf import settings

@login_required
def dashboard(request):
    user_invoices = Invoice.objects.filter(user=request.user)  # assuming Invoice model has a user field
    return render(request, 'invoices/dashboard.html', {'invoices': user_invoices})

@login_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    invoice.delete()
    return redirect('dashboard')

@login_required
def download_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    file_path = os.path.join(settings.MEDIA_ROOT, invoice.file.name)
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type="application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
