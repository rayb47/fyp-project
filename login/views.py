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
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView


# Create your views here.
def home(request):
    print("BOOMBOOMBOOM")
    return render(request, "login/index.html")

def signup(request):

    if request.method == 'POST':
        print("Inside the post")
        prof_level = 0
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        study_frequency = request.POST.get('frequencyUnit')
        study_frequency_amount = request.POST.get('studyFrequency')
        beginner_lvl = request.POST.get('beginner_lvl')
        intermediate_lvl = request.POST.get('intermediate_lvl')
        advanced_lvl = request.POST.get('advanced_lvl')
        
        language_yes = request.POST.get('languageYes')
        language_no = request.POST.get('languageNo')
        # Collect form data
        form_data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'confirm_password': request.POST.get('confirmPassword'),
            'study_frequency': request.POST.get('frequencyUnit'),
            'study_frequency_amount': request.POST.get('studyFrequency'),
            'beginner_lvl': request.POST.get('beginner_lvl'),
            'intermediate_lvl': request.POST.get('intermediate_lvl'),
            'advanced_lvl': request.POST.get('advanced_lvl'),
            'language_yes': request.POST.get('languageYes'),
            'language_no': request.POST.get('languageNo'),
        }

        # print("username:", username, "email:", email, "password:", password)
        # print("study_frequency:", study_frequency, "study_frequency_amount:", study_frequency_amount)
        # print(beginner_lvl, intermediate_lvl, advanced_lvl, language_yes, language_no)

        # Check if the username already exists
        if CustomUser.objects.filter(username=form_data['username']).exists():
            messages.error(request, "Username already exists")
            # Render the template with form_data to repopulate the form fields
            return render(request, 'login/signup.html', {'form_data': form_data})
        
        
        # subject = 'Hello'
        # message = 'Hello there. This is an email message.'
        # email_from = settings.EMAIL_HOST_USER
        # recipient_list = ['raynellb47@gmail.com',]
        # send_mail( subject, message, email_from, recipient_list )


        try:
            #myuser = CustomUser.objects.create_user(username=username, email=email, password=password)
            myuser = CustomUser(username=username, email=email)
            myuser.set_password(password)
            myuser.is_active = False
        except Exception as e:
            print("Couldn't create user object")
            print(e)
            return
        
        myuser = CustomUser(username=username, email=email)
        myuser.set_password(password)
        myuser.is_active = False

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
            myuser.save()
            print("User Saved YESSSS")
        except Exception as e:
            print(e)
            print("Inside the except")
            return
        
        # Generate and send activation email
        current_site = get_current_site(request)
        mail_subject = 'Activate your account on MySite'
        message = render_to_string('login/acc_active_email.html', {
            'user': myuser,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': account_activation_token.make_token(myuser),
        })
        send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [email])
        return HttpResponse('Please confirm your email address to complete the registration')


        messages.success(request, "Account successfully created!")



        return redirect('login:signin')


    return render(request, "login/signup.html")

def signin(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = False
        print(username, password)

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if remember_me == True:
                print("Remember me is TRUE")
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                 request.session.set_expiry(0)
            print("good")
            request.session['uname'] = username
            #return render(request, "mainsite/dashboard.html", {'uname': username})
            return redirect('mainsite:home')
        else:
            messages.error(request, "Invalid credentials.")
            print("bad")
            return redirect('login:signin')


    return render(request, "login/signin.html")

def signout(request):
    pass

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # Log the user in and redirect to home page
        login(request, user)
        return redirect('mainsite:home')
    else:
        return HttpResponse('Activation link is invalid!')
    
class MyPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

def password_reset(request):
    print("Inside password reset view")
    email = request.POST.get('email', None)
    print("Associated email is:",email)
    user = CustomUser.objects.get(email=email,username='ray3')
    print(user)
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
        send_mail(subject, email, settings.EMAIL_HOST_USER , [user.email], fail_silently=False)
    except Exception as e:
        return JsonResponse({'error': 'Email could not be sent'}, status=500)
    return JsonResponse({'success': 'Password reset link has been sent to your email'}, status=200)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'login/custom_password_reset_confirm.html'  # Path to your custom template
    success_url = '/signin'  # URL to redirect after a successful password reset