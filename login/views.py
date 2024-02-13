from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from login.models import CustomUser


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
        
        

        try:
            myuser = CustomUser.objects.create_user(username=username, email=email, password=password)
        except Exception as e:
            print("Couldn't create user object")
            print(e)
            return

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
        except:
            print("Inside the except")
            return

        messages.success(request, "Account successfully created!")

        return redirect('login:signin')


    return render(request, "login/signup.html")

def signin(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
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
