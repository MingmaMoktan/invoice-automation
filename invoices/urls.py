from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('upload/', views.upload_invoice, name='upload_invoice'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
]
