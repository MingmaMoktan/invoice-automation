from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Static pages
    path('', views.landing, name='landing'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Blog
    path('blog/', views.blog, name='blog'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),

    # Invoice OCR
    path('upload/', views.upload_invoice, name='upload_invoice'),  # single upload
    path('upload-multiple/', views.upload_invoices, name='upload_invoices'),  # multi-upload
    path('download-csv/', views.download_invoices_csv, name='download_invoices_csv'),  # CSV download
    
    # Authentication
    path('signup/', views.signup, name='signup'),

    #For users
    path('dashboard/', views.dashboard, name='dashboard'),
    path('invoice/<int:invoice_id>/delete/', views.delete_invoice, name='delete_invoice'),
    path('invoice/<int:invoice_id>/download/', views.download_invoice, name='download_invoice'),
    
    #For Pans
    path("select-plan/<str:plan>/", views.select_plan, name="select_plan"),
    path("payment/<str:plan>/", views.payment_page, name="payment_page"),
]
