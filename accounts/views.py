from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm
from .models import User


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration submitted. Await admin approval.")
            return redirect("login")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_approved:
                messages.error(request, "Account pending approval.")
                return render(request, "accounts/login.html")

            login(request, user)
            return redirect("/reports/dashboard/")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "accounts/login.html")

def user_logout(request):
    """Log the user out and redirect to login page."""
    logout(request)
    return redirect('login')