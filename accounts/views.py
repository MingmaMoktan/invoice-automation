from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .forms import CustomAuthenticationForm

def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})
