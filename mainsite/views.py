from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from login.models import CustomUser
import requests

# Create your views here.
def home(request):
    r = requests.get("http://api.weatherapi.com/v1/current.json?key=023566f8135543a68ab235213233012&q=Lisbon")
    r = r.json()
    print(r)
    data = {
        'uname': request.session.get('uname'),
        'city': r['location']['name'],
        'country': r['location']['country'],
        'local_time': r['location']['localtime'],
        'temp_c': str(r['current']['temp_c']) + '°C',
        'image': r['current']['condition']['icon']
    }
    print("Data:", data)
    return render(request, "mainsite/dashboard.html", data)

def signout(request):
    print("Inside the signout view")
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login:signin')

def quiz(request):
    submitted_answer = request.session.get('submitted_answer', '')
    source_view = request.session.get('source_view')

    print("Loading the quiz page!")
    print("Quiz submitted value is:", submitted_answer)
    print("Source view is:", source_view)
    return render(request, 'mainsite/quiz_1.html', {'quiz': submitted_answer, 'source_view': source_view})

# Include different messages for answering questions correctly
# Include scrollbar for different temperatures in cities for portugal - scrolls automatically
# Include public holidays for Portugal
# Change greeting to 'Good afternoon/morning' based on local time
def submit_answer(request):
    valu = ''
    is_correct = False
    if request.method == 'POST':
        submitted_answer = request.POST.get('quiz')
        valu = submitted_answer
        if submitted_answer == 'maca':
            is_correct = True
        print("Submitted answer:",submitted_answer)
        if not submitted_answer:
            messages.info(request, 'Please select an answer!')
            return redirect('mainsite:quiz')
        if is_correct:
            messages.success(request, 'Correct Answer!')
        else:
            messages.error(request, 'Incorrect Answer, Try again!')
    else:
        print("This is not a post request!!!!!!!!!!!")
    request.session['submitted_answer'] = valu
    request.session['source_view'] = 'submitted_answer'
    return redirect('mainsite:quiz')
    return render(request, 'mainsite/quiz_1.html', {'quiz': valu})