from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home_view(request):
    # This view will now catch and clear any pending "Logout" messages
    return render(request, "home.html")


def about_view(request):
    return render(request, "about.html")


def contact_view(request):
    return render(request, "contact.html")


def products_view(request):
    return render(request, "products.html")


@login_required
def profile_view(request):
    if request.method == "POST":
        if "change_password" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully!")
                return redirect("profile")
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            if first_name and last_name:
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.save()
                messages.success(request, "Profile details updated!")
            return redirect("profile")

    password_form = PasswordChangeForm(request.user)
    return render(request, "profile.html", {"password_form": password_form})
