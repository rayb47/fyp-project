from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from login.models import CustomUser
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_str
from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

# View to handle registration of a new user
def signup(request):
    # Handles post requests
    if request.method == 'POST':
        # Picks up inputted form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('passwordConfirm')
        study_frequency = request.POST.get('frequencyUnit')
        study_frequency_amount = request.POST.get('studyFrequency')
        beginner_lvl = request.POST.get('beginner_lvl')
        intermediate_lvl = request.POST.get('intermediate_lvl')
        advanced_lvl = request.POST.get('advanced_lvl')
        language_yes = request.POST.get('languageYes')
        language_no = request.POST.get('languageNo')

        # Check if the username already exists
        if CustomUser.objects.filter(username=email).exists():
            msg = "Username already exists!"
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        # Check if the email is already registered to an account
        if CustomUser.objects.filter(email=email).exists():
            msg = "Email is already registered with an account!"
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        
        # Verifies passwords match
        if password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match'}, status=400)
        
        # Validates inputted password
        try:
            validate_password(password)
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': e.messages}, status=400)

        try:
            myuser = CustomUser(username=username, email=email)
            myuser.set_password(password)
            myuser.is_active = False
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Technical error'}, status=400)
        
        myuser = CustomUser(username=username, email=email)
        myuser.set_password(password)
        myuser.is_active = False

        # Sets user attributes based on inputted data
        if study_frequency and study_frequency_amount:
            myuser.study_frequency = study_frequency
            myuser.study_frequency_amount = study_frequency_amount
        if language_yes:
            myuser.portuguese_default = True
        if language_no:
            myuser.portuguese_default = False
        if beginner_lvl:
            myuser.proficiency_level = 1
        if intermediate_lvl:
            myuser.proficiency_level = 2
        if advanced_lvl:
            myuser.proficiency_level = 3
        try:
            # Saves created user object
            myuser.save()

            # Defining attributes for email to be sent out
            current_site = get_current_site(request)    
            subject = 'Activate your account on PortuPro'
            from_email = settings.EMAIL_HOST_USER
            protocol = 'https' if settings.USE_HTTPS else 'http'
            to = [email]
            text_content = 'Please confirm your email address to complete the registration.'
            html_content = render_to_string('login/acc_active_email.html', {
                'user': myuser,
                'domain': f'{protocol}://{current_site.domain}',
                'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                'token': account_activation_token.make_token(myuser),
            })
            email = EmailMultiAlternatives(subject, text_content, from_email, to)
            email.attach_alternative(html_content, "text/html")
            # Sends out the email
            email.send()
            # Prompts the user to check their email
            return JsonResponse({'status': 'success', 'message': 'Please confirm your email address to complete the registration'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
    return render(request, "login/signup.html")

# View to handle signing in
def signin(request):
    # Handles post requests
    if request.method == 'POST':
        # Picks up the entered username and password
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticates the entered user credentials
        user = authenticate(username=username, password=password)
        # If login is successful, redirect user to landing page. Else, display an error message and refresh signin page.
        if user is not None:
            login(request, user)
            return redirect('mainsite:home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login:signin')
    
    # Renders signin page
    return render(request, "login/signin.html")

# Handles activation link for account registration
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # Saves and redirects user to login screen after account activation
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login:signin')
    else:
        return HttpResponse('Activation link is invalid!')

# Handles password reset 
class MyPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

# Handles sending out email for a password reset
def password_reset(request):
    email = request.POST.get('email', None)
    user = CustomUser.objects.get(email=email,username='rayb13')
    subject = "Password Reset Requested"
    email_template_name = "login/password_reset_subject.txt"
    current_site = get_current_site(request)
    c = {
    "email":user.email,
    'domain':current_site.domain,
    'site_name': 'Website',
    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
    "user": user,
    'token': default_token_generator.make_token(user),
    'protocol': 'http',
    }
    email = render_to_string(email_template_name, c)
    try:
        # Sends the email
        send_mail(subject, email, settings.EMAIL_HOST_USER , [user.email], fail_silently=False)
    except Exception:
        return JsonResponse({'error': 'Email could not be sent'}, status=500)
    # Prompts the user to check email
    return JsonResponse({'success': 'Password reset link has been sent to your email'}, status=200)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    # Path to your custom template
    template_name = 'login/custom_password_reset_confirm.html' 
    # URL to redirect after a successful password reset
    success_url = '/signin'  