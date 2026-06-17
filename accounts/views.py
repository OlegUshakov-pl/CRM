import logging
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import LoginForm, ProfileForm, PasswordChangeForm

logger = logging.getLogger(__name__)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next') or ''
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect('core:dashboard')
            form.add_error(None, 'Invalid username or password')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if 'password_submit' in request.POST:
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data['new_password'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                request.session.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('accounts:profile')
        elif 'profile_submit' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                return redirect('accounts:profile')
    else:
        profile_form = ProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    return render(request, 'accounts/profile.html', {'form': profile_form, 'password_form': password_form})
