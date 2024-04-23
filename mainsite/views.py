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
from django.utils.dateformat import DateFormat
import os
import time
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment
import random
from django.core import serializers
from mainsite.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.db.models import Count, Case, When, IntegerField
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models.functions import TruncDate
from datetime import date
from django.utils import translation
import csv
# Include message for streak
# Include English Text to Portuguese using the TTS

# Create your views here.

from django.utils import timezone

def test_session(request):
    now = timezone.now()
    formatted_now = now.isoformat()
    request.session['test_time'] = formatted_now
    
    retrieved_time = request.session.get('test_time', None)
    return HttpResponse(f"Stored time: {formatted_now}, Retrieved time: {retrieved_time}")

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

    user_activity_dates = [
    DateFormat(date).format('Y-m-d') for date in UserActivity.objects.filter(
        user=request.user,
        date__lt=date.today() 
    ).values_list('date', flat=True).distinct()
    ]
    print(user_activity_dates)
    print("IN HOME REQUEST")
    combined_city_data = []
    # Units
    units = Unit.objects.all()    

    dates_with_more_than_five_answers = UserAnswers.objects.filter(user=request.user) \
        .annotate(answer_day=TruncDate('answer_date')) \
        .values('answer_day') \
        .annotate(answer_count=Count('id')) \
        .filter(answer_count__gt=5) \
        .values_list('answer_day', flat=True) \
        .order_by('answer_day')
    formatted_goal_dates = [date.strftime('%Y-%m-%d') for date in dates_with_more_than_five_answers]
    print(formatted_goal_dates)

    r = requests.get("http://api.weatherapi.com/v1/current.json?key=023566f8135543a68ab235213233012&q=Lisbon")
    r = r.json()
    current_hour = int(r['location']['localtime'].split(' ')[1].split(':')[0])
    current_date = r['location']['localtime'].split(' ')[0]


    # for city_name in ['Porto', 'Madeira']:
    #     res = requests.get("https://api.weatherapi.com/v1/current.json?key=023566f8135543a68ab235213233012&q={}".format(city_name))
    #     res = res.json()
    #     combined_city_data.append({
    #         'city': city_name,
    #         'temp_c': str(res['current']['temp_c']) + '°C',
    #         # 'image': res['current']['condition']['icon'],
    #     })
    # print("Combined city data is:", combined_city_data)

    greeting = ''
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    print("Local time variable:", type(current_date))
    date_obj = datetime.strptime(current_date, '%Y-%m-%d')
    added_suffix = ''
    if 4 <= date_obj.day <= 20 or 24 <= date_obj.day <= 30:
        added_suffix = str(date_obj.day) + "th"
    else:
        added_suffix = str(date_obj.day) + ["st", "nd", "rd"][date_obj.day % 10 - 1]
    current_date = f"{added_suffix} {date_obj.strftime('%B')}, {date_obj.year}"
    data = {
        'uname': request.session.get('uname'),
        'city': r['location']['name'],
        'country': r['location']['country'],
        'current_date': current_date,
        'temp_c': str(r['current']['temp_c']) + '°C',
        'image': r['current']['condition']['icon'],
        'greeting': greeting,
        'units': units,
        'combined_city_data': combined_city_data,
        'user_activity_dates': user_activity_dates,
        'goal_dates': formatted_goal_dates
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

def media(request):
    return render(request, 'mainsite/media.html')

def get_incorrect_questions(request, unit_id):
    questions_data = {
        '1': [
            {'question': 'What is the capital of Portugal?', 'type': 'Multiple Choice', 'answer': 'Lisbon', 'correctAnswer': 'Lisbon'},
            {'question': 'Translate "dog" to Portuguese.', 'type': 'Translation', 'answer': 'Cãooo', 'correctAnswer': 'Cão'}
        ],
        # Add cases for other units
    }
    answer_data = []
    for item in UserAnswers.objects.filter(user=request.user, question__quiz__unit=int(unit_id), is_correct=False):
        answer_data.append(
            {'question': item.question.question_text,
             'type': item.question.question_type,
             'answer': item.answer_text,
             'correctAnswer': item.question.correct_answer}
        )

    # questions = questions_data.get(unit_id, [])
    return JsonResponse({'questions': answer_data})

def quiz4(request):
    answer_status = request.session.get('answer_status', None)
    print("Answer status:", answer_status)
    return render(request, 'mainsite/quiz_4.html', {'answer_status': answer_status})

def get_unit_details(request, unit_id):
    # Example data, replace with actual query to your database or data source
    unit_details = {
        'title': f'Unit {unit_id} Analytics',
        'details': [
            {'icon': 'check-circle', 'text': 'Correct Answers', 'value': 20, 'color': 'text-success'},
            {'icon': 'times-circle', 'text': 'Incorrect Answers', 'value': 5, 'color': 'text-danger'},
            # more details...
        ]
    }
    return JsonResponse(unit_details)

def analytics(request):
    word_count_studied = 0
    correct_count = UserAnswers.objects.filter(user=request.user, is_correct=True).count()
    incorrect_count = UserAnswers.objects.filter(user=request.user, is_correct=False).count()
    lessons_done = UserAttempts.objects.filter(user=request.user, lesson__isnull=False)
    for lesson in lessons_done:
        word_count_studied = 2 * int(lesson.pages_covered-1)

    main_data = {}
    for unit in Unit.objects.all():
        correct = UserAnswers.objects.filter(user=request.user, is_correct=True, question__quiz__unit=int(unit.id)).count()
        incorrect = UserAnswers.objects.filter(user=request.user, is_correct=False, question__quiz__unit=int(unit.id)).count()
        attempted = UserAnswers.objects.filter(user=request.user, question__quiz__unit=int(unit.id)).count()
        quizzes_done = UserAttempts.objects.filter(user=request.user, quiz__isnull=False, questions_answered=8, quiz__unit=int(unit.id)).count()
        lessons = UserAttempts.objects.filter(user=request.user, lesson__isnull=False, lesson__unit=int(unit.id))
        if lessons.count() > 0:
            word_count = 2*(lessons[0].pages_covered-1)
        else:
            word_count = 0

        detail_list = [
            {'icon': 'check-circle', 'text': 'Correct Answers', 'value': correct, 'color': 'text-success'},
            {'icon': 'times-circle', 'text': 'Incorrect Answers', 'value': incorrect, 'color': 'text-danger'},
            {'icon': 'question-circle', 'text': 'Questions Attempted', 'value': attempted, 'color': 'text-info'},
            {'icon': 'trophy', 'text': 'Quizzes Completed', 'value': quizzes_done, 'color': 'text-warning'},
            {'icon': 'book-open', 'text': 'Words/Phrases Learnt', 'value': word_count, 'color': 'text-secondary'}
        ]
        main_data[str(unit.id)] = {
            'title': f'Unit {unit.id} Analytics',
            'details': detail_list
        }

    print("Main Data:", main_data)
    correct_answers = UserAnswers.objects.filter(is_correct=True, user=request.user).annotate(
    unit_id=Case(
        When(attempt__lesson__isnull=False, then='attempt__lesson__unit'),
        When(attempt__quiz__isnull=False, then='attempt__quiz__unit'),
        output_field=IntegerField(),
    )
    ).values('unit_id').annotate(correct_count=Count('id')).order_by('-correct_count')
    incorrect_answers = UserAnswers.objects.filter(is_correct=False, user=request.user).annotate(
    unit_id=Case(
        When(attempt__lesson__isnull=False, then='attempt__lesson__unit'),
        When(attempt__quiz__isnull=False, then='attempt__quiz__unit'),
        output_field=IntegerField(),
    )
    ).values('unit_id').annotate(incorrect_count=Count('id')).order_by('-incorrect_count')
    
    best_unit = Unit.objects.get(id=correct_answers.first()['unit_id']).name if correct_answers.first() else 'None'
    worst_unit = Unit.objects.get(id=incorrect_answers.first()['unit_id']).name if incorrect_answers.first() else 'None'

    data = {
        'total_correct_answers':correct_count,
        'total_incorrect_answers':incorrect_count,
        'total_words_studied':word_count_studied,
        'best_unit': best_unit,
        'worst_unit': worst_unit,
        'total_data': main_data
    }

    return render(request, 'mainsite/analytics.html', data)

def download_table(request):
    if request.method == 'POST':
        table_data = request.POST.getlist('table_data[]')

        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')  # Note the charset change to 'utf-8-sig'
        response['Content-Disposition'] = 'attachment; filename="saved-words.csv"'

        writer = csv.writer(response)
        writer.writerow(['No.', 'Portuguese', 'English', 'English Example Usage', 'Portuguese Example Usage'])
        for row in table_data:
            columns = row.split(',')
            # Make sure to handle the Unicode strings properly by ensuring they are in the correct format
            writer.writerow([col for col in columns])

        return response

@login_required
def delete_all_saved_words(request):
    # Assuming you have a function to delete items, adapt as necessary.
    try:
        # Your deletion logic here
        # Item.objects.filter(user=request.user).delete()
        UserSavedWords.objects.filter(user=request.user).delete()
        return JsonResponse({"success": True}, status=200)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def settings(request):
    return render(request, 'mainsite/settings.html')


@login_required
def architecture(request):
    if request.user.is_authenticated:
        if request.user.portuguese_default:
            print("I NEED PORTUGUESE")
            translation.activate('pt')  # Activate Portuguese
            request.session['django_language'] = 'pt'  # Correctly set the language key in the session
        else:
            translation.deactivate_all()  # or activate a default language
    return render(request, 'mainsite/architecture.html')

@login_required
def festivals(request):
    return render(request, 'mainsite/festivals.html')

@login_required
def testdiacritics(request):
    return render(request, 'mainsite/test_diacritics.html')

@login_required
def diacritics(request):
    return render(request, 'mainsite/diacritics.html')

@login_required
def vocab_search(request):
    # ADD VALIDATION FOR PASSING BLANK STRINGS IF NONSENSE IS INPUTTED
    query = request.GET.get('query',None)
    print("Inside vocab general view")
    # Translation API 
    url = "https://text-translator2.p.rapidapi.com/translate"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "7223147287mshb3ab5722c178634p1818bbjsn832d911c373c",
        "X-RapidAPI-Host": "text-translator2.p.rapidapi.com"
    }
    payload = {
                "source_language": "en",
                "target_language": "pt",
                "text": query
            }
    translation_response = requests.post(url, data=payload, headers=headers)


    return JsonResponse({'words': [{'english': query, 'portuguese': translation_response.json()['data']['translatedText']}]}, safe=False)

@login_required
def vocab(request):
    # FILTER OVERALL WORD DISPLAY BASED ON UNIT
    search_query = request.GET.get('query', None)
    search = request.GET.get('search', False)
    user_id = request.user.id
    user_saved_words = UserSavedWords.objects.filter(user=user_id).order_by('-id')
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

    if not UserAttempts.objects.filter(lesson=lesson, user=request.user).exists():
        UserAttempts.objects.create(lesson=lesson, user=request.user)
    else:
        user_attempt = UserAttempts.objects.get(lesson=lesson, user=request.user)
        user_attempt.pages_covered = int(page)
        user_attempt.save()
    
    example_usages_1 = words[0].example_usages.all()
    word_1_usages = []
    word_1_usages.append(example_usages_1)
    try:
        example_usages_2 = words[1].example_usages.all()
    except:
        example_usages_2 = []
    word_2_usages = []
    word_2_usages.append(example_usages_2)

    return render(request, 'mainsite/lesson.html', {'lesson': lesson, 'words': words, 'word_1_usages':word_1_usages, 'word_2_usages':word_2_usages})


@login_required
@csrf_exempt
def save_word(request):

    word_type = request.POST.get('word_type', 'custom')
    custom_english = request.POST.get('english', None)
    custom_portuguese = request.POST.get('portuguese', None)
    is_correct = True
    word_id = request.POST.get('word_id')
    add_or_remove = request.POST.get('add_or_remove', 'add')
    
    if add_or_remove == 'add':
        if word_type == 'custom':
            try:
                UserSavedWords.objects.get(user=request.user, custom_english=custom_english)
            except:
                UserSavedWords.objects.create(
                    user=request.user,
                    custom_english=custom_english,
                    custom_portuguese=custom_portuguese
                )
        else:
            print("TRYING TO ADD A WORD")
            try:
                print("Inside the try block")
                UserSavedWords.objects.get(word_id=word_id)
                return JsonResponse({'is_correct': False, "message": "Word already in the list!"}, status=400)
            except:
                print("Inside the except block")
                UserSavedWords.objects.create(
                    user=request.user,
                    word=Word.objects.get(id=int(word_id))
                )
    else:
        a = 1
        UserSavedWords.objects.get(id=word_id).delete()
            
        print("INSIDE DELETING A SAVED WORD!")

    print("WORD SAVED HELL YEAH")
    return JsonResponse({'is_correct': is_correct, "message": "Word successfull saved!"}, status=200)

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

    question_obj = Question.objects.filter(question_type='Arrange')[0]
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
    quizzes = []
    unit_id = request.GET.get('unit_id')
    quiz_data = Quiz.objects.filter(unit_id=int(unit_id))
    quiz_number = 0
    for quiz in quiz_data:
        total_questions = quiz.questions.all().count() 
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

        tts = gTTS(text, lang=language, slow=True)

        # Save the generated speech to an audio file
        tts.save("output.mp3")

         # Load the speech audio
        sound = AudioSegment.from_file("output.mp3")

        # Change speed of the audio
        speed = 1.2  # Speed factor > 1 to increase speed
        altered_frame_rate = int(sound.frame_rate * speed)
        faster_sound = sound._spawn(sound.raw_data, overrides={"frame_rate": altered_frame_rate})
        faster_sound = faster_sound.set_frame_rate(sound.frame_rate)

        # Save the faster audio
        faster_sound.export("output_fast.mp3", format="mp3")

        # Initialize the mixer
        pygame.mixer.init()

        # Load and play the audio file
        pygame.mixer.music.load("output_fast.mp3")
        pygame.mixer.music.play()

        # Wait until the audio has finished playing
        while pygame.mixer.music.get_busy():
            time.sleep(2)
            
        # Stop the mixer
        pygame.mixer.music.stop()

        # Quit the mixer
        pygame.mixer.quit()

        try:
            # Remove the audio file if it exists
            if os.path.isfile("output_fast.mp3"):
                os.remove("output_fast.mp3")
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

        # Return a simple JSON response indicating success
        return JsonResponse({'status': 'success', 'message': 'Text has been converted to speech.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt  # Disable CSRF for simplicity (you should handle CSRF properly in production)
def process_audio(request):
    try:
        if request.method == 'POST':
            result = ''
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
                    result = 'success'
                    
                else:
                    result = 'error'
                    
            if os.path.exists('converted_audio.wav'):
                os.remove('converted_audio.wav')
            return JsonResponse({'status': result, 'transcript': text})

            

    except sr.UnknownValueError:
        return JsonResponse({'status': 'error', 'message': 'Could not understand audio'})
    except sr.RequestError as e:
        return JsonResponse({'status': 'error', 'message': f'Could not request results; {e}'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})