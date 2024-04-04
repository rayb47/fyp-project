from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from login.models import CustomUser
from mainsite.models import Unit
import requests
import speech_recognition as sr
from django.http import JsonResponse
from gtts import gTTS
import pygame
import os
import time
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment
import random
from mainsite.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

# Include message for streak
# Include English Text to Portuguese using the TTS

# Create your views here.

def weather_data(request):
    data = []
    cities = ['Lisbon', 'Madeira']
    for city in cities:
        r = requests.get("https://api.weatherapi.com/v1/current.json?key=023566f8135543a68ab235213233012&q={}".format(city))
        r = r.json()
        current_date = r['location']['localtime'].split(' ')[0]
        data.append(
            {
                'city': r['location']['name'],
                'current_date': current_date,
                'temp_c': str(r['current']['temp_c']) + '°C',
            }
        )
    return JsonResponse({'data': data})

    

def home(request):

    # Units
    units = Unit.objects.all()    

    r = requests.get("http://api.weatherapi.com/v1/current.json?key=023566f8135543a68ab235213233012&q=Lisbon")
    r = r.json()
    print(r['location']['localtime'])
    current_hour = int(r['location']['localtime'].split(' ')[1].split(':')[0])
    current_date = r['location']['localtime'].split(' ')[0]
    print("Hour:", current_hour)
    greeting = ''
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    data = {
        'uname': request.session.get('uname'),
        'city': r['location']['name'],
        'country': r['location']['country'],
        'local_time': current_date,
        'temp_c': str(r['current']['temp_c']) + '°C',
        'image': r['current']['condition']['icon'],
        'greeting': greeting,
        'units': units
    }
    
    for unit in units:
        print(unit.name, unit.id, unit.description)
        
    return render(request, "mainsite/test_dashboard.html", data)

def signout(request):
    print("Inside the signout view")
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login:signin')

def quiz2(request):
    return render(request, 'mainsite/quiz_2.html')

def quiz3(request):
    return render(request, 'mainsite/quiz_3.html')

def quiz4(request):
    answer_status = request.session.get('answer_status', None)
    print("Answer status:", answer_status)
    return render(request, 'mainsite/quiz_4.html', {'answer_status': answer_status})


def architecture(request):
    return render(request, 'mainsite/architecture.html')

def lesson(request, lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    words_list = lesson.word_set.all()

    # Define the number of words per page
    words_per_page = 2

    # Get the 'page' GET parameter, which indicates the current page
    page = request.GET.get('page', 1)  # Default to the first page

    # Create a Paginator object with your words and the number of words per page
    paginator = Paginator(words_list, words_per_page)

    try:
        words = paginator.page(page)
    except PageNotAnInteger:
        # If the 'page' parameter is not an integer, show the first page
        words = paginator.page(1)
    except EmptyPage:
        # If the 'page' parameter is out of range (e.g., 9999), show the last page of results
        words = paginator.page(paginator.num_pages)

    return render(request, 'mainsite/quiz_6.html', {'lesson': lesson, 'words': words})

def quiz(request, unit_id, quiz_id):
    # Image API
    api_key = 'TD3tzuMg9GoBdmw2QLf2jrheWlkp9L91Hk1DXyUtVuIWzrkadRZXv1o2'
    # The Pexels API endpoint for searching photos
    image_url = 'https://api.pexels.com/v1/search'
    # Set up the headers with your API key
    image_headers = {
        'Authorization': api_key
    }



    # Translation API 
    url = "https://text-translator2.p.rapidapi.com/translate"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "7223147287mshb3ab5722c178634p1818bbjsn832d911c373c",
        "X-RapidAPI-Host": "text-translator2.p.rapidapi.com"
    }
    # return render(request, 'mainsite/quiz_2.html')
    number = random.randint(1, 9)
    water_img = ''
    options = {}
    img_links = []
    question_obj = Question.objects.get(id=number)
    # question_obj = Question.objects.get(id=number)
    question_obj = Question.objects.last()
    print("Inside quiz view.")
    print("Question:", question_obj.question_text)
    jumbled_answer = []

    if question_obj.question_type == 'MCQ':
        options_list = question_obj.option_set.all()
        for option in options_list:
            print("Options:", option)
            payload = {
                "source_language": "pt",
                "target_language": "en",
                "text": option
            }
            translation_response = requests.post(url, data=payload, headers=headers)
            #print("English option:", translation_response.json()['data']['translatedText'])
            image_params = {
                'query': translation_response.json()['data']['translatedText'],  # The search term you're looking for
                'per_page': 10,     # Number of results per page
                'page': 1           # Page number (if you want to implement pagination)
            }
            image_response = requests.get(image_url, headers=image_headers, params=image_params)
            photo = image_response.json()['photos'][0]['src']['original']

            image_response = requests.get('https://pixabay.com/api/?key=40135184-dc7bf4341a3143778714e9097&q={}'.format(option))
            data = image_response.json()
            options[option] = photo
    elif question_obj.question_type == 'MCQ_Text':
        options_list = question_obj.option_set.all()
        options = options_list
    elif question_obj.question_type == 'Arrange':
        jumbled_answer = question_obj.correct_answer.split(" ")
        random.shuffle(jumbled_answer)
    elif question_obj.question_type == 'Translate':
        a = 1

    submitted_answer = request.session.get('submitted_answer', '')
    source_view = request.session.get('source_view')
    unit_name = question_obj.quiz.unit.name
    unit_id = question_obj.quiz.unit.id

    image_response = requests.get(f'https://pixabay.com/api/?key=40135184-dc7bf4341a3143778714e9097&q=water')
    

    if image_response.status_code == 200:
        data = image_response.json()
        water_img = data['hits'][0]['webformatURL']
    else:
        print(f'Error: {image_response.status_code}')
    #     # Process the data as needed
    #     # For example, you can access the image URLs using data['hits'][0]['webformatURL']
    # else:
    #     print(f'Error: {response.status_code}')

    # --------------------------
    print("Inside the quiz view!")
    
    template_name = 'mainsite/quiz_1.html'
    if question_obj.question_type == 'Speech':
        template_name = 'mainsite/quiz_2.html'
    if question_obj.question_type == 'Match':
        template_name = 'mainsite/quiz_3.html'
    if question_obj.question_type == 'MCQ_Text':
        template_name = 'mainsite/quiz_4.html'
    if question_obj.question_type == 'MCQ':
        template_name = 'mainsite/quiz_1.html'
    if question_obj.question_type == 'Arrange':
        template_name = 'mainsite/quiz_5.html'
    if question_obj.question_type == 'Translate':
        template_name = 'mainsite/quiz_6.html'


    return render(request, template_name, {
        'quiz': submitted_answer, 
        'source_view': source_view, 
        'question_text': question_obj.question_text, 
        'question_answer': question_obj.correct_answer,
        'question_id': question_obj.id,
        'water_img': water_img,
        'unit_name': unit_name,
        'unit_id': unit_id,
        'options': options,
        'jumbled_answer': jumbled_answer
    })

# Include different messages for answering questions correctly
# Include scrollbar for different temperatures in cities for portugal - scrolls automatically
# Include public holidays for Portugal
# Change greeting to 'Good afternoon/morning' based on local time
def submit_answer(request):
    print("Inside submit answer")
    valu = ''
    is_correct = False
    submitted_answer = request.POST.get('quiz')
    correct_ans_msgs = ['Correct Answer!','Well Done!','Spot on!','You got it!']
    success_msg = random.choice(correct_ans_msgs)

    form_type = request.POST.get('form_type')
    question_id = request.POST.get('form_type')
    try:
        question_obj = Question.objects.get(id=int(question_id))
    except:
        pass
    print("Inside the submit_answer view!")
    print("Question ID:", question_id)
    print("Correct answer:",question_obj.correct_answer)
    print("Submitted Answer:", submitted_answer)
    if question_obj.question_type == 'Arrange':
        submitted_answer = json.loads(submitted_answer)
        sentence = ' '.join(submitted_answer)
        print("Submitted sentence:", sentence)
        if sentence == question_obj.correct_answer:
            is_correct = True
            print("Arrange answer is correct")
        return JsonResponse({'is_correct': is_correct, "message": "Correct answer!"}, status=200)

    else:
        if (question_obj.correct_answer).lower() == submitted_answer.lower():
            is_correct = True
            return JsonResponse({'is_correct': is_correct, "message": "Correct answer!"}, status=200)
        else:
            return JsonResponse({'is_correct': is_correct, "message": "Incorrect! OH NO!"}, status=200)

    if form_type == 'form_a':
        print("Inside form A type:", form_type)
        is_correct = False
        if request.method == 'POST':
            submitted_answer = request.POST.get('quiz')
            valu = submitted_answer
            if submitted_answer == 'maçã':
                is_correct = True
                print("Inside is correct True")
                return JsonResponse({'is_correct': is_correct, "message": "Correct answer!"}, status=200)
            else:
                
                return JsonResponse({'is_correct': is_correct, "message": "Incorrect! OH NO!"}, status=200)
            # print("Submitted answer:",submitted_answer)
            # if not submitted_answer:
            #     messages.info(request, 'Please select an answer!')
            #     return redirect('mainsite:quiz')
            # if is_correct:
            #     messages.success(request, success_msg)
            # else:
            #     messages.error(request, 'Incorrect Answer')
        else:
            print("This is not a post request!!!!!!!!!!!")
        request.session['submitted_answer'] = valu
        request.session['source_view'] = 'submitted_answer'
        # return redirect('mainsite:quiz')
        # return render(request, 'mainsite/quiz_1.html', {'quiz': valu})
        # return JsonResponse({'answer_status': answer_status}, status=200)
        # return redirect('mainsite:quiz4')
        # return render(request, 'mainsite/quiz_4.html')
        

@csrf_exempt  # Disable CSRF token for simplicity (not recommended for production)
def text_to_speech(request):
    # This will only work with POST requests
    if request.method == 'POST':
        text = request.POST.get('text', '')
        language = 'pt'  # Set the language to Portuguese

        tts = gTTS(text, lang=language)

        # Save the generated speech to an audio file
        tts.save("output.mp3")

        # Initialize the mixer
        pygame.mixer.init()

        # Load and play the audio file
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()

        # Wait until the audio has finished playing
        while pygame.mixer.music.get_busy():
            time.sleep(2)

        # # Clean up the audio file
        # os.remove("output.mp3")
            
        # Stop the mixer
        pygame.mixer.music.stop()

        # Quit the mixer
        pygame.mixer.quit()

        try:
            # Remove the audio file if it exists
            if os.path.isfile("output.mp3"):
                os.remove("output.mp3")
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

        # Return a simple JSON response indicating success
        return JsonResponse({'status': 'success', 'message': 'Text has been converted to speech.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt  # Disable CSRF for simplicity (you should handle CSRF properly in production)
def process_audio(request):
    try:
        if request.method == 'POST':
            audio_file = request.FILES['audio']
            file_name = audio_file.name
            file_extension = os.path.splitext(file_name)[1]

            # Convert audio to WAV format using pydub
            audio = AudioSegment.from_file(audio_file, format=file_extension.replace('.', ''))
            audio = audio.set_frame_rate(16000).set_channels(1)  # Convert to mono and adjust frame rate
            audio.export("converted_audio.wav", format="wav")

            # Use the converted audio file for recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile("converted_audio.wav") as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language='pt-BR')
                if text == "eu sou um menino":
                    return JsonResponse({'status': 'success', 'transcript': text})
                else:
                    return JsonResponse({'status': 'error', 'transcript': text})

            

    except sr.UnknownValueError:
        return JsonResponse({'status': 'error', 'message': 'Could not understand audio'})
    except sr.RequestError as e:
        return JsonResponse({'status': 'error', 'message': f'Could not request results; {e}'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})