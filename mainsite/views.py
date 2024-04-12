from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from login.models import CustomUser
from mainsite.models import Unit
import requests
import speech_recognition as sr
from random import shuffle
from django.http import JsonResponse
from gtts import gTTS
import pygame
import os
import time
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment
import random
from django.core import serializers
from mainsite.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
# Include message for streak
# Include English Text to Portuguese using the TTS

# Create your views here.

@login_required
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

    

@login_required
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

def analytics(request):
    return render(request, 'mainsite/analytics.html')

def settings(request):
    return render(request, 'mainsite/settings.html')


@login_required
def architecture(request):
    return render(request, 'mainsite/architecture.html')

@login_required
def vocab(request):
    search_query = request.GET.get('query', None)
    search = request.GET.get('search', False)
    user_id = request.user.id
    user_saved_words = UserSavedWords.objects.filter(user=user_id)
    if search == 'True':
        words = Word.objects.filter(portuguese_word__icontains=search_query)
        print("Words inside filter:",words)
        print("Search term is:",search)
    else:
        words = Word.objects.all()
    return render(request, 'mainsite/vocab.html', {'saved_words': user_saved_words, 'words': words})

@login_required
def search_word(request):
    search_query = request.GET.get('query', None)
    words = Word.objects.filter(
    Q(portuguese_word__icontains=search_query) | 
    Q(english_translation__icontains=search_query)
)

    # Serialize the words along with their example usages
    words_data = []
    for word in words:
        # Getting the first example usage for simplicity; adjust according to your needs
        example_usage = word.example_usages.first()  
        words_data.append({
            'id': word.id,
            'portuguese_word': word.portuguese_word,
            'english_translation': word.english_translation,
            'example_usage': {
                'english_usage': example_usage.english_usage if example_usage else '',
                'portuguese_usage': example_usage.portuguese_usage if example_usage else '',
            }
        })

    return JsonResponse({'words': words_data})

@login_required
def store_page_number(request):
    page = request.POST.get('page_number',None)
    lesson_id = request.POST.get('lesson_id',None)
    print("Next page number is:",page)
    print("Lesson ID is:",lesson_id)
    lesson_obj = Lesson.objects.get(id=int(lesson_id))
    if not UserAttempts.objects.filter(lesson=lesson_obj, user=request.user).exists():
        UserAttempts.objects.create(lesson=lesson_obj, user=request.user)
    else:
        user_attempt = UserAttempts.objects.get(lesson=lesson_obj, user=request.user)
        user_attempt.pages_covered = int(page)-1
        user_attempt.save()


    return JsonResponse({'is_correct': True, "message": "Word successfully saved!"}, status=200)

@login_required
def lesson(request, lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    words_list = lesson.word_set.all()


    default = 1
    if UserAttempts.objects.filter(lesson=lesson, user=request.user).exists():
        print("Inside check!!!!!s")
        print(UserAttempts.objects.filter(lesson=lesson, user=request.user))
        default = int(UserAttempts.objects.filter(lesson=lesson, user=request.user)[0].pages_covered)

    # Define the number of words per page
    words_per_page = 2

    # Get the 'page' GET parameter, which indicates the current page
    page = request.GET.get('page', default)  # Default to the first page

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
    print("WORDS:",words.__dict__)

    if not UserAttempts.objects.filter(lesson=lesson, user=request.user).exists():
        UserAttempts.objects.create(lesson=lesson, user=request.user)
    else:
        user_attempt = UserAttempts.objects.get(lesson=lesson, user=request.user)
        user_attempt.pages_covered = int(page)
        user_attempt.save()

    usage_dict = {}
    test = {
        'word': {
            'english_usage': [],
            'portuguese_usage': []
        }
    }
    
    example_usages_1 = words[0].example_usages.all()
    word_1_usages = []
    word_1_usages.append(example_usages_1)
    try:
        example_usages_2 = words[1].example_usages.all()
    except:
        example_usages_2 = []
    word_2_usages = []
    word_2_usages.append(example_usages_2)
    
    # for word in words:
    #     example_usages = word.example_usages.all()
    #     print("EXU:",example_usages)
    #     print(word)
    #     usages = ExampleUsage.objects.get(word=word)
        
    #     print(usages)

    


    return render(request, 'mainsite/lesson.html', {'lesson': lesson, 'words': words, 'word_1_usages':word_1_usages, 'word_2_usages':word_2_usages})


@login_required
def save_word(request):
    data = {
        'key': 'value',
    }
    is_correct = True
    word_id = request.POST.get('word_id')
    add_or_remove = request.POST.get('add_or_remove', 'add')
    
    if add_or_remove == 'add':
        try:
            UserSavedWords.objects.get(word_id=word_id)
            print("SAVED WORD NOT ADDED")
        except:
            UserSavedWords.objects.create(
                user=request.user,
                word=Word.objects.get(id=int(word_id))
            )
    else:
        a = 1
        print("INSIDE DELETING A SAVED WORD!")


    return JsonResponse({'is_correct': is_correct, "message": "Word successfully saved!"}, status=200)

@login_required
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
    # To get all questions for quiz 1 of unit 1
    # Quiz.objects.filter(unit_id=1)[0].questions.all()
    number = random.randint(1, 11)
    water_img = ''
    question_obj = None
    repeated_question = False
    options = {}
    img_links = []
    match_dict = {}
    left_col_q = []
    right_col_q = []
    # print(Quiz.objects.filter(unit_id=unit_id)[quiz_id-1].questions.all())
    quiz_accessed = Quiz.objects.filter(unit_id=unit_id)[quiz_id-1]
    questions_for_quiz = quiz_accessed.questions.all()
    print(quiz_accessed.questions.all())
    print(quiz_accessed.__dict__)
    if UserAttempts.objects.filter(quiz=quiz_accessed, user=request.user).exists():
        print("This quiz has been accessed")
        user_attempt = UserAttempts.objects.filter(quiz=quiz_accessed, user=request.user)[0]
    else:
        user_attempt = UserAttempts.objects.create(quiz=quiz_accessed, user=request.user)
        print("This quiz has not been accessed")
    
    # if unit_id == 2:
    #     question_obj = Question.objects.get(id=number)
    # else:
    #     question_obj = Question.objects.get(id=number)
    # question_obj = Question.objects.get(id=number)
    # question_obj = Question.objects.last()
    jumbled_answer = []
    questions_not_answered_correctly = []
    unanswered_questions = Question.objects.filter(
        quiz_id=quiz_id
    ).exclude(
        id__in=UserAnswers.objects.filter(
            question__quiz_id=quiz_id,
            user=request.user
        ).values_list('question_id', flat=True)
    )

    
    # questions_answered_correctly_twice = UserAnswers.objects.filter(
    #     question__quiz_id=quiz_id,
    #     user_id=request.user,
    #     is_correct=True
    # ).values(
    #     'question_id'
    # ).annotate(
    #     correct_count=Count('id')
    # ).filter(
    #     correct_count__gte=2
    # ).values_list('question_id', flat=True)
        
    print("Number of incorrect answers in this quiz are:",UserAnswers.objects.filter(attempt=user_attempt, user=request.user, is_correct=False).count())
    if unanswered_questions:
        if user_attempt.questions_answered > 3 and random.randint(1,100) <= 20:
            answered_questions = Question.objects.filter(
                quiz_id=quiz_id,
                id__in=UserAnswers.objects.filter(
                    question__quiz_id=quiz_id,
                    user=request.user
                ).values_list('question_id', flat=True)
            )
            answered_questions_list = list(answered_questions)
            question_obj = random.choice(answered_questions_list)
            repeated_question = True
        else:
            question_obj = unanswered_questions.first()
    else:
        repeated_question = True
        print("All questions have been answered once.")
        print(questions_for_quiz)
        # Loops through questions for the quiz
        questions_for_quiz_copy = list(questions_for_quiz)
        shuffle(questions_for_quiz_copy)
        for question in questions_for_quiz_copy:
            print(UserAnswers.objects.filter(attempt=user_attempt, user=request.user, question=question, is_correct=True))
            # Checks if questions that haven't been answered corrrectly yet exist, if so, displays one of those next.
            if not UserAnswers.objects.filter(attempt=user_attempt, user=request.user, question=question, is_correct=True).exists():
                question_obj = question
                break
                repeated_question = True
            # elif UserAnswers.objects.filter(attempt=user_attempt, user=request.user, question=question, is_correct=True).count() < 2:
            #     print("Inside less than 2 check")
            #     question_obj = question
            #     break
            else:
                print("Inside the else")
        if not question_obj:
            return render(request, 'mainsite/cube.html')
        # user_answer = UserAnswers.objects.filter(attempt=user_attempt, user=request.user, is_correct=False)[0]
        # number = random.randint(1, 11)
        # question_obj = Question.objects.get(quiz=quiz_accessed, id=number)
        # question_obj = user_answer.question
    print("Unanswered questions are:", unanswered_questions)

    question_obj = Question.objects.filter(question_type='MCQ')[0]
    if question_obj.question_type == 'MCQ':
        options_list = question_obj.option_set.all()
        for option in options_list:
            print("Options:", option)
            word = Word.objects.get(portuguese_word=option)
            # payload = {
            #     "source_language": "pt",
            #     "target_language": "en",
            #     "text": option
            # }
            # translation_response = requests.post(url, data=payload, headers=headers)
            #print("English option:", translation_response.json()['data']['translatedText'])
            # image_params = {
            #     'query': translation_response.json()['data']['translatedText'],  # The search term you're looking for
            #     'per_page': 10,     # Number of results per page
            #     'page': 1           # Page number (if you want to implement pagination)
            # }
            image_params = {
                'query': word.english_translation,
                'per_page': 10,
                'page': 1
            }
            # image_response = requests.get(image_url, headers=image_headers, params=image_params)
            # photo = image_response.json()['photos'][0]['src']['original']
            photo = "https://buffer.com/library/content/images/size/w1200/2023/10/free-images.jpg"
            # image_response = requests.get('https://pixabay.com/api/?key=40135184-dc7bf4341a3143778714e9097&q={}'.format(option))
            # data = image_response.json()
            options[option] = photo
    elif question_obj.question_type == 'MCQ_Text':
        options_list = question_obj.option_set.all()
        options = options_list
    elif question_obj.question_type == 'Arrange':
        jumbled_answer = question_obj.correct_answer.split(" ")
        random.shuffle(jumbled_answer)
    elif question_obj.question_type == 'Translate':
        a = 1
    elif question_obj.question_type == 'Match':
        matches = question_obj.match_set.all()
        for match in matches:
            left_col_q.append(match.left_option)
            right_col_q.append(match.right_option)
            match_dict[match.left_option] = match.right_option
        print(match_dict)
        random.shuffle(left_col_q)
        random.shuffle(right_col_q)
            

    submitted_answer = request.session.get('submitted_answer', '')
    unit_name = question_obj.quiz.unit.name
    unit_id = question_obj.quiz.unit.id

    # image_response = requests.get(f'https://pixabay.com/api/?key=40135184-dc7bf4341a3143778714e9097&q=water')
    

    # if image_response.status_code == 200:
    #     data = image_response.json()
    #     water_img = data['hits'][0]['webformatURL']
    # else:
    #     print(f'Error: {image_response.status_code}')
    #     # Process the data as needed
    #     # For example, you can access the image URLs using data['hits'][0]['webformatURL']
    # else:
    #     print(f'Error: {response.status_code}')

    # --------------------------
    
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
        'question_text': question_obj.question_text, 
        'question_answer': question_obj.correct_answer,
        'question_id': question_obj.id,
        'water_img': water_img,
        'unit_name': unit_name,
        'unit_id': unit_id,
        'options': options,
        'jumbled_answer': jumbled_answer,
        'match_items': match_dict,
        'left_col_q':left_col_q,
        'right_col_q': right_col_q,
        'repeated_question': repeated_question,
    })

# Include different messages for answering questions correctly
# Include scrollbar for different temperatures in cities for portugal - scrolls automatically
# Include public holidays for Portugal
# Change greeting to 'Good afternoon/morning' based on local time
@login_required
def submit_answer(request):
    print("Inside the submit answer view")
    valu = ''
    is_correct = False
    first_time = True
    submitted_answer = request.POST.get('quiz')
    question_id = request.POST.get('form_type')
    question_type = request.POST.get('question_type', None)
    correct_ans_msgs = ['Correct Answer!','Well Done!','Spot on!','You got it!']
    success_msg = random.choice(correct_ans_msgs)
    testing = False
    try:
        question_obj = Question.objects.get(id=int(question_id))
    except:
        pass
    try:
        user_attempt = UserAttempts.objects.get(quiz=question_obj.quiz, user=request.user, questions_answered__lt=12)
    except:
        testing = True
    if UserAnswers.objects.filter(question=question_obj, user=request.user, is_correct=True).exists():
        first_time = False
    # print("Number of incorrect answers in this quiz are:",UserAnswers.objects.filter(attempt=user_attempt, user=request.user, is_correct=False).count())
    # print("USER ATTEMPT:",user_attempt)
    if question_obj.question_type in ['Match', 'Speech']:
        is_correct = True
    elif question_obj.question_type == 'Arrange':
        submitted_answer = json.loads(submitted_answer)
        sentence = ' '.join(submitted_answer)
        print("Submitted sentence:", sentence)
        if sentence == question_obj.correct_answer:
            is_correct = True
            print("Arrange answer is correct")
        # return JsonResponse({'is_correct': is_correct, "message": "Correct answer!"}, status=200)
    else:
        if (question_obj.correct_answer).lower() == submitted_answer.lower():
            is_correct = True
        #     return JsonResponse({'is_correct': is_correct, "message": "Correct answer!"}, status=200)
        # else:
        #     return JsonResponse({'is_correct': is_correct, "message": "Incorrect! OH NO!"}, status=200)
    if is_correct == True:
        if testing == False:
            try:
                UserAnswers.objects.create(attempt=user_attempt, user=request.user, question=question_obj, answer_text=submitted_answer, is_correct=is_correct)
            except:
                UserAnswers.objects.create(attempt=user_attempt, user=request.user, question=question_obj, answer_text=question_obj.correct_answer, is_correct=is_correct)

            if first_time == True:
                user_attempt.questions_answered += 1  # increment by 1
                user_attempt.save()
        return JsonResponse({'is_correct': is_correct, "message": success_msg}, status=200)
    else:
        if testing == False:
            UserAnswers.objects.create(attempt=user_attempt, user=request.user, question=question_obj, answer_text=submitted_answer, is_correct=is_correct)
        return JsonResponse({'is_correct': is_correct, "message": "Incorrect! OH NO!"}, status=200)
    
@login_required
def get_quiz_data(request):
    print("Inside get_quiz_data")
    quizzes = []
    unit_id = request.GET.get('unit_id')
    quiz_data = Quiz.objects.filter(unit_id=int(unit_id))
    quiz_number = 0
    for quiz in quiz_data:
        print("FEGEGE",UserAnswers.objects.filter(user=request.user, question__in=quiz.questions.all(), is_correct=True).count())
        total_questions = quiz.questions.all().count() 
        print("Total questions:",total_questions)
        questions_answered = UserAnswers.objects.filter(user=request.user, question__in=quiz.questions.all(), is_correct=True).values('question').distinct().count()
        quiz_number += 1
        quizzes.append({
            'id': quiz.id,
            'total_questions': total_questions,
            'questions_answered': questions_answered,
            'progress_percent': int(( questions_answered / total_questions ) * 100) if total_questions > 0 else 0,
            'number': quiz_number
        })

    return JsonResponse({'quizzes': quizzes})
        

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