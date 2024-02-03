from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django_email_verification import send_email

from django.views.generic import TemplateView

from authentication.forms import LoginForm, RegisterForm


def login_user(request):
    context = {'login_form': LoginForm()}
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user:
                login(request, user)
                return redirect('index')
            else:
                context = {
                    'login_form': login_form,
                    'attention': f'The user with username {email} and password was not found!'
                }
        else:
            context = {
                'login_form': login_form
            }
    return render(request, 'auth/login.html', context)


def register_user(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save(commit=False)
            user_email = form.cleaned_data['email']
            user_username = form.cleaned_data['username']
            user_password = form.cleaned_data['password1']
            # Create new user
            user = User.objects.create_user(username=user_username, email=user_email, password=user_password)

            # Make user unactive until they click link to token in email
            user.is_active = False
            send_email(user)
            return HttpResponseRedirect(reverse('login'))


    return render(request, 'auth/register.html', {'user_form': form})

'''class RegisterView(TemplateView):
    template_name = 'auth/register.html'

    def get(self, request):
        user_form = RegisterForm()
        context = {'user_form': user_form}
        return render(request, 'auth/register.html', context)

    def post(self, request):
        user_form = RegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            login(request, user)
            return redirect('index')

        context = {'user_form': user_form}
        return render(request, 'auth/register.html', context)'''


def logout_user(request):
    logout(request)
    return redirect('index')
