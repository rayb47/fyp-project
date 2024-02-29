from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from login.models import CustomUser
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

# Include message for streak
# Include English Text to Portuguese using the TTS

# Create your views here.
def home(request):
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
        'greeting': greeting
    }
    print("Data:", data)
    return render(request, "mainsite/dashboard.html", data)

def signout(request):
    print("Inside the signout view")
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login:signin')

def quiz2(request):
    return render(request, 'mainsite/quiz_2.html')

def quiz3(request):
    return render(request, 'mainsite/quiz_3.html')

def quiz(request):
    # return render(request, 'mainsite/quiz_2.html')
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
    correct_ans_msgs = ['Correct Answer!','Well Done!','Spot on!','You got it!']
    success_msg = random.choice(correct_ans_msgs)

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
            messages.success(request, success_msg)
        else:
            messages.error(request, 'Incorrect Answer')
    else:
        print("This is not a post request!!!!!!!!!!!")
    request.session['submitted_answer'] = valu
    request.session['source_view'] = 'submitted_answer'
    return redirect('mainsite:quiz')
    return render(request, 'mainsite/quiz_1.html', {'quiz': valu})


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

            return JsonResponse({'status': 'success', 'transcript': text})

    except sr.UnknownValueError:
        return JsonResponse({'status': 'error', 'message': 'Could not understand audio'})
    except sr.RequestError as e:
        return JsonResponse({'status': 'error', 'message': f'Could not request results; {e}'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})