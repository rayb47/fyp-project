from django.shortcuts import redirect, render
from django.http import HttpResponse
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
import ast
from django.utils.dateformat import DateFormat
import os
from datetime import timedelta
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
from django.db.models import OuterRef, Subquery
from django.db.models.functions import TruncDate
from datetime import date
from django.utils import translation
import csv
from django.utils import timezone

# Renders the Home Page
@login_required
def home(request):
    
    # Dates a user has been active for more than the set activity goal (10 minutes by default)
    user_activity_dates = [
    DateFormat(date).format('Y-m-d') for date in UserActivity.objects.filter(
        user=request.user,
        date__lt=date.today() 
    ).values_list('date', flat=True).distinct()
    ]

    # Dates a user has answered more than 5 questions
    question_goal = request.user.daily_question_goal
    formatted_goal_dates = []
    if question_goal > 0:
        dates_with_more_than_five_answers = UserAnswers.objects.filter(user=request.user) \
            .annotate(answer_day=TruncDate('answer_date')) \
            .values('answer_day') \
            .annotate(answer_count=Count('id')) \
            .filter(answer_count__gt=5) \
            .values_list('answer_day', flat=True) \
            .order_by('answer_day')
        formatted_goal_dates = [date.strftime('%Y-%m-%d') for date in dates_with_more_than_five_answers]
        
    # All existing units
    units = Unit.objects.all() 
       
    r = requests.get("http://api.weatherapi.com/v1/current.json?key=023566f8135543a68ab235213233012&q=Lisbon")
    r = r.json()
    current_date = r['location']['localtime'].split(' ')[0]
    current_hour = int(r['location']['localtime'].split(' ')[1].split(':')[0])

    combined_city_data = []
    for city_name in ['Porto', 'Madeira']:
        res = requests.get("https://api.weatherapi.com/v1/current.json?key=023566f8135543a68ab235213233012&q={}".format(city_name))
        res = res.json()
        combined_city_data.append({
            'city': city_name,
            'temp_c': str(res['current']['temp_c']) + '°C',
            'image': res['current']['condition']['icon'],
        })

    # Set type of greeting based on time of day
    greeting = ''
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Edit date to appropriate format to be displayed (Format Example: 13th January, 2024)
    date_obj = datetime.strptime(current_date, '%Y-%m-%d')
    added_suffix = ''
    if 4 <= date_obj.day <= 20 or 24 <= date_obj.day <= 30:
        added_suffix = str(date_obj.day) + "th"
    else:
        added_suffix = str(date_obj.day) + ["st", "nd", "rd"][date_obj.day % 10 - 1]
    current_date = f"{added_suffix} {date_obj.strftime('%B')}, {date_obj.year}"

    # Data to be passed to the template
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

    # Render the home page template   
    return render(request, "mainsite/test_dashboard.html", data)

# Signs out a user from the website
def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    # Redirect to the login page
    return redirect('login:signin')

def media(request):
    return render(request, 'mainsite/media.html')

# Fetches data on the incorrect answers for a particular unit
def get_incorrect_questions(request, unit_id):
    answer_data = []
    for item in UserAnswers.objects.filter(user=request.user, question__quiz__unit=int(unit_id), is_correct=False):
        if item.question.question_type == 'Arrange':
            actual_list = ast.literal_eval(item.answer_text)
            print(type(actual_list), actual_list)
            formulated_string = ' '.join(actual_list)
        answer_data.append(
            {'question': item.question.question_text,
             'type': item.question.question_type,
             'answer': formulated_string if item.question.question_type == 'Arrange' else item.answer_text,
             'correctAnswer': item.question.correct_answer}
        )

    # Returns the data in JSON format to be displayed on the frontend
    return JsonResponse({'questions': answer_data})

def analytics(request):
    # Computes the necessary data and renders the Analytics Page
    word_count_studied = 0
    correct_count = UserAnswers.objects.filter(user=request.user, is_correct=True).count()
    incorrect_count = UserAnswers.objects.filter(user=request.user, is_correct=False).count()
    lessons_done = UserAttempts.objects.filter(user=request.user, lesson__isnull=False)
    for lesson in lessons_done:
        pg_covered = 1 if lesson.pages_covered == 0 else lesson.pages_covered
        word_count_studied = 2 * int(pg_covered-1)

    # Get the current time
    now = timezone.now()

    # Correct and Incorrect answers for last day, week, and month
    correct_last_day = UserAnswers.objects.filter(user=request.user, is_correct=True, answer_date__gte=now - timedelta(days=1)).count()
    incorrect_last_day = UserAnswers.objects.filter(user=request.user, is_correct=False, answer_date__gte=now - timedelta(days=1)).count()
    correct_last_week = UserAnswers.objects.filter(user=request.user, is_correct=True, answer_date__gte=now - timedelta(weeks=1)).count()
    incorrect_last_week = UserAnswers.objects.filter(user=request.user, is_correct=False, answer_date__gte=now - timedelta(weeks=1)).count()
    correct_last_month = UserAnswers.objects.filter(user=request.user, is_correct=True, answer_date__gte=now - timedelta(days=30)).count()
    incorrect_last_month = UserAnswers.objects.filter(user=request.user, is_correct=False, answer_date__gte=now - timedelta(days=30)).count()

    # Filter to get active user dates
    user_activity_dates = [
    DateFormat(date).format('Y-m-d') for date in UserActivity.objects.filter(
        user=request.user,
        date__lt=date.today() 
    ).values_list('date', flat=True).distinct()
    ]

    # Adding formulated data for each unit to main_data dictionary
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

        # Statistics to be displayed
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

    # Finding best and worst performing unit
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

    # Data to be sent to the template
    data = {
        'total_correct_answers':correct_count,
        'total_incorrect_answers':incorrect_count,
        'total_words_studied':word_count_studied,
        'best_unit': best_unit,
        'worst_unit': worst_unit,
        'total_data': main_data,
        'correct_last_day': correct_last_day,
        'incorrect_last_day': incorrect_last_day,
        'correct_last_week': correct_last_week,
        'incorrect_last_week': incorrect_last_week,
        'correct_last_month': correct_last_month,
        'incorrect_last_month': incorrect_last_month,
        'active_user_dates': len(user_activity_dates)
    }

    return render(request, 'mainsite/analytics.html', data)

def download_table(request):
    # Writes the content of the User Saved Vocabulary to CSV file
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
    # Deletes all user saved words
    try:
        UserSavedWords.objects.filter(user=request.user).delete()
        return JsonResponse({"success": True}, status=200)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def settings(request):
    # Renders the Settings page
    return render(request, 'mainsite/settings.html')

@login_required
def architecture(request):
    # Renders the Festivals page
    if request.user.is_authenticated:
        if request.user.portuguese_default:
            translation.activate('pt')
        else:
            translation.deactivate_all()
    return render(request, 'mainsite/architecture.html')

@login_required
def festivals(request):
    # Renders the Architecture page
    if request.user.is_authenticated:
        if request.user.portuguese_default:
            translation.activate('pt')  # Activate Portuguese
            request.session['django_language'] = 'pt'
        else:
            translation.deactivate_all()
    return render(request, 'mainsite/festivals.html')

def submit_feedback(request):
    # Saves user feedback
    feedback = request.POST.get('feedback')
    UserFeedback.objects.get_or_create(user=request.user, feedback=feedback)
    return JsonResponse({"message": 'Thank you for your feedback!'})


@login_required
def diacritics(request):
    # Renders the Diacritics page
    return render(request, 'mainsite/diacritics.html')

@login_required
def save_settings(request):
    # Saves edited user settings
    if request.user.is_authenticated:
        current_user_id = request.user.id
        current_user_object = CustomUser.objects.get(id=current_user_id)
        data = request.POST.get('dataToSend', None)
        if data:
            data = json.loads(data)
            if 'siteLanguage' in data:
                current_user_object.portuguese_default = True if data['siteLanguage'] == 'Portuguese' else False
            if 'dailyGoalMinutes' in data:
                current_user_object.daily_activity_goal = int(data['dailyGoalMinutes'])
            if 'dailyGoalQuestions' in data:
                current_user_object.daily_question_goal = int(data['dailyGoalQuestions'])
            if 'playbackSpeed' in data:
                current_user_object.playback_speed = data['playbackSpeed']
            current_user_object.save()
    
    return JsonResponse({'words': 'Data edited successfully!'})

# Finds equivalent Portuguese for the inputted English phrase/word
@login_required
def vocab_search(request):
    query = request.GET.get('query',None)
    # Translation API application
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

# Displays the Vocabulary List
@login_required
def vocab(request):
    # Filters overall word list and displays result
    search_query = request.GET.get('query', None)
    search = request.GET.get('search', False)
    user_id = request.user.id
    user_saved_words = UserSavedWords.objects.filter(user=user_id).order_by('-id')
    if search == 'True':
        words = Word.objects.filter(portuguese_word__icontains=search_query)
    else:
        words = Word.objects.all()
    return render(request, 'mainsite/vocab.html', {'saved_words': user_saved_words, 'words': words})

# Carries out the dynamic search over the Vocabulary List
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
        # Getting the first example usage to display in the table
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
    # Stores current page number in the lesson
    page = request.POST.get('page_number',None)
    lesson_id = request.POST.get('lesson_id',None)
    lesson_obj = Lesson.objects.get(id=int(lesson_id))
    if not UserAttempts.objects.filter(lesson=lesson_obj, user=request.user).exists():
        UserAttempts.objects.create(lesson=lesson_obj, user=request.user, pages_covered=0)
    else:
        user_attempt = UserAttempts.objects.get(lesson=lesson_obj, user=request.user)
        user_attempt.pages_covered = int(page)-1
        user_attempt.save()

    return JsonResponse({'is_correct': True, "message": "Word successfully saved!"}, status=200)

@login_required
def lesson(request, lesson_id):
    proficiency_dict = {
        '1': 'Beginner',
        '2': 'Intermediate',
        '3': 'Advanced'
    }
    lesson = Lesson.objects.get(unit_id=lesson_id, difficulty=proficiency_dict[str(request.user.proficiency_level)])
    words_list = lesson.word_set.all()

    # Page number variable
    default = 1
    if UserAttempts.objects.filter(lesson=lesson, user=request.user).exists():
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

    percent_complete = int((int(page)/paginator.num_pages)*100)

    # Sets current page in the lesson for the user
    if not UserAttempts.objects.filter(lesson=lesson, user=request.user).exists():
        UserAttempts.objects.create(lesson=lesson, user=request.user, pages_covered=0)
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

    unit_obj = Unit.objects.get(id=lesson_id)

    return render(request, 'mainsite/lesson.html', {
        'lesson': lesson, 'words': words, 'word_1_usages':word_1_usages, 'word_2_usages':word_2_usages, 
        'percent_complete': percent_complete, 'unit_id': lesson_id, 'unit_name': unit_obj.name})


@login_required
@csrf_exempt
def save_word(request):
    # Variable definitions
    word_type = request.POST.get('word_type', 'custom')
    custom_english = request.POST.get('english', None)
    custom_portuguese = request.POST.get('portuguese', None)
    is_correct = True
    word_id = request.POST.get('word_id')
    add_or_remove = request.POST.get('add_or_remove', 'add')
    
    # Code to add words to the user saved list
    if add_or_remove == 'add':
        if word_type == 'custom':
            # If word is not already saved, create a new UserSavedWords object (for custom words)
            try:
                UserSavedWords.objects.get(user=request.user, custom_english=custom_english)
            except:
                UserSavedWords.objects.create(
                    user=request.user,
                    custom_english=custom_english,
                    custom_portuguese=custom_portuguese
                )
        else:
            # If word is not already saved, create a new UserSavedWords object (for lesson words)
            try:
                UserSavedWords.objects.get(word_id=word_id, user=request.user)
                return JsonResponse({'is_correct': False, "message": "Word already in the list!"}, status=400)
            except:
                UserSavedWords.objects.create(
                    user=request.user,
                    word=Word.objects.get(id=int(word_id))
                )
    else:
        UserSavedWords.objects.get(id=word_id).delete()
    return JsonResponse({'is_correct': is_correct, "message": "Word successfull saved!"}, status=200)

@login_required
def quiz(request, unit_id, quiz_id):
    # User set difficulty
    difficulty_dict = {
        '1': 'Beginner',
        '2': 'Intermediate',
        '3': 'Advanced'
    }
    difficulty = difficulty_dict[str(request.user.proficiency_level)]
    
    # PexelsAPI Setup
    api_key = 'TD3tzuMg9GoBdmw2QLf2jrheWlkp9L91Hk1DXyUtVuIWzrkadRZXv1o2'
    image_url = 'https://api.pexels.com/v1/search'
    image_headers = {
        'Authorization': api_key
    }

    # Variabe definitions
    question_obj = None
    repeated_question = False
    options = {}
    match_dict = {}
    left_col_q = []
    right_col_q = []
    jumbled_answer = []

    # Set quiz to be accessed
    quiz_accessed = Quiz.objects.filter(unit_id=unit_id, difficulty=difficulty)[quiz_id-1]
    questions_for_quiz = quiz_accessed.questions.all()

    # Check if user has already attempted the quiz
    if UserAttempts.objects.filter(quiz=quiz_accessed, user=request.user).exists():
        print("User has already attempted the quiz")
        user_attempt = UserAttempts.objects.filter(quiz=quiz_accessed, user=request.user).order_by('-attempt_date')[0]
        if user_attempt.questions_answered == 8:
            print("User has answered all questions")
            print("Creating user object")
            user_attempt = UserAttempts.objects.create(quiz=quiz_accessed, user=request.user, questions_answered=0)
            messages.success(request, 'Quiz complete!')
            # Redirect to home screen if user has completed a quiz
            return redirect('mainsite:home')
    else:
        user_attempt = UserAttempts.objects.create(quiz=quiz_accessed, user=request.user, questions_answered=0)
    
    # Finding unanswered questions in the quiz
    unanswered_questions = Question.objects.filter(
        quiz_id=quiz_id
    ).exclude(
        id__in=UserAnswers.objects.filter(
            question__quiz_id=quiz_id,
            user=request.user,
            attempt=user_attempt
        ).values_list('question_id', flat=True)
    )

    # Finding questions whose latest answer is incorrect
    latest_incorrect_answer_subquery = UserAnswers.objects.filter(
        question=OuterRef('pk'),
        is_correct=False,
        user=request.user,
        attempt = user_attempt
    ).order_by('-answer_date').values('id')[:1]
    # Query to find questions where the latest answer is incorrect
    questions_with_latest_incorrect_answer = Question.objects.annotate(
        latest_incorrect_answer_id=Subquery(latest_incorrect_answer_subquery)
    ).filter(
        user_answers__id=Subquery(latest_incorrect_answer_subquery)  # Ensures we filter on the latest incorrect answer
    ).values_list('id', flat=True)  # Get the IDs of those questions
    list_of_question_ids = list(questions_with_latest_incorrect_answer)

    # Loop through unanswered questions in the Quiz
    if unanswered_questions:
        if user_attempt.questions_answered > 3 and random.randint(1,100) <= 20:
            answered_questions = Question.objects.filter(
                quiz_id=quiz_id,
                id__in=UserAnswers.objects.filter(
                    question__quiz_id=quiz_id,
                    user=request.user,
                    attempt = user_attempt
                ).values_list('question_id', flat=True)
            )
            answered_questions_list = list(answered_questions)
            question_obj = random.choice(answered_questions_list)
            repeated_question = True
        else:
            question_obj = unanswered_questions.first()
    else:
        repeated_question = True
        if len(list_of_question_ids) > 0:
            for question_id in list_of_question_ids:
                question_obj = Question.objects.get(id=question_id)
                break
        
        # Loops through questions for the quiz
        questions_for_quiz_copy = list(questions_for_quiz)
        shuffle(questions_for_quiz_copy)
        for question in questions_for_quiz_copy:
            print(UserAnswers.objects.filter(attempt=user_attempt, user=request.user, question=question, is_correct=True))
            # Checks if questions that haven't been answered corrrectly yet exist, if so, displays one of those next.
            if not UserAnswers.objects.filter(attempt=user_attempt, user=request.user, question=question, is_correct=True).exists():
                question_obj = question
                break
    
    # Question comprehension for each question type
    if question_obj.question_type == 'MCQ':
        options_list = question_obj.option_set.all()
        for option in options_list:
            word = Word.objects.get(portuguese_word=option)
            image_params = {
                'query': word.english_translation,
                'per_page': 10,
                'page': 1
            }
            image_response = requests.get(image_url, headers=image_headers, params=image_params)
            photo = image_response.json()['photos'][0]['src']['original']
            options[option] = photo
    elif question_obj.question_type == 'MCQ_Text':
        options_list = question_obj.option_set.all()
        options = options_list
    elif question_obj.question_type == 'Arrange':
        jumbled_answer = question_obj.correct_answer.split(" ")
        random.shuffle(jumbled_answer)
    elif question_obj.question_type == 'Translate':
        pass
    elif question_obj.question_type == 'Match':
        matches = question_obj.match_set.all()
        for match in matches:
            left_col_q.append(match.left_option)
            right_col_q.append(match.right_option)
            match_dict[match.left_option] = match.right_option
        random.shuffle(left_col_q)
        random.shuffle(right_col_q)
            
    submitted_answer = request.session.get('submitted_answer', '')
    unit_name = question_obj.quiz.unit.name
    unit_id = question_obj.quiz.unit.id
    
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
        'unit_name': unit_name,
        'unit_id': unit_id,
        'options': options,
        'jumbled_answer': jumbled_answer,
        'match_items': match_dict,
        'left_col_q':left_col_q,
        'right_col_q': right_col_q,
        'repeated_question': repeated_question,
    })

@login_required
def submit_answer(request):
    # Variable definitions
    is_correct = False
    submitted_answer = request.POST.get('quiz')
    question_id = request.POST.get('form_type')
    correct_ans_msgs = ['Correct Answer!','Well Done!','Spot on!','You got it!']
    success_msg = random.choice(correct_ans_msgs)

    # Defining question object and user attempt
    question_obj = Question.objects.get(id=int(question_id))
    user_attempt = UserAttempts.objects.filter(quiz=question_obj.quiz, user=request.user).order_by('-attempt_date')[0]
    
    # Checking answer correctness
    if question_obj.question_type in ['Match', 'Speech']:
        is_correct = True
    elif question_obj.question_type == 'Arrange':
        submitted_answer = json.loads(submitted_answer)
        sentence = ' '.join(submitted_answer)
        if sentence == question_obj.correct_answer:
            is_correct = True
    else:
        if (question_obj.correct_answer).lower() == submitted_answer.lower():
            is_correct = True
    if is_correct:
        try:
            UserAnswers.objects.create(attempt=user_attempt, user=request.user, question=question_obj, answer_text=submitted_answer, is_correct=is_correct)
        except:
            UserAnswers.objects.create(attempt=user_attempt, user=request.user, question=question_obj, answer_text=question_obj.correct_answer, is_correct=is_correct)
        # Increasing user attempt count
        user_attempt.questions_answered += 1
        user_attempt.save()
        return JsonResponse({'is_correct': is_correct, "message": success_msg}, status=200)
    else:
        UserAnswers.objects.create(attempt=user_attempt, user=request.user, question=question_obj, answer_text=submitted_answer, is_correct=is_correct)
        return JsonResponse({'is_correct': is_correct, "message": "Incorrect! OH NO!"}, status=200)
    
@login_required
def get_quiz_data(request):
    # Variable definitions
    quizzes = []
    unit_id = request.GET.get('unit_id')
    proficiency_dict = {
        '1': 'Beginner',
        '2': 'Intermediate',
        '3': 'Advanced'
    }
    quiz_data = Quiz.objects.filter(unit_id=int(unit_id), difficulty=proficiency_dict[str(request.user.proficiency_level)])
    quiz_number = 0
    # Looping through quizzes for a unit
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
    # Returns quiz data
    return JsonResponse({'quizzes': quizzes})
        

@csrf_exempt
def text_to_speech(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        # Sets the language to Portuguese
        language = 'pt'
        tts = gTTS(text, lang=language, slow=True)

        # Save the generated speech to an audio file
        tts.save("output.mp3")

        # Load the speech audio
        sound = AudioSegment.from_file("output.mp3")
        # Fetching set user playback speed
        playback = CustomUser.objects.get(id=request.user.id).playback_speed
        if playback == 'Normal':
            playback_speed = 1.0
        elif playback == 'Slow':
            playback_speed = 0.9
        else:
            playback_speed = 1.1

        # Change speed of the audio
        speed = playback_speed
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
            if os.path.isfile("output.mp3"):
                os.remove("output.mp3")
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

        # Return a simple JSON response indicating success
        return JsonResponse({'status': 'success', 'message': 'Text has been converted to speech.'})
    # Return a simple JSON response indicating failure
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt
def process_audio(request, question_id):
    # Processes audio generated by the user
    try:
        if request.method == 'POST':
            result = ''
            audio_file = request.FILES['audio']
            file_name = audio_file.name
            file_extension = os.path.splitext(file_name)[1]

            question_obj = Question.objects.get(id=question_id)

            # Convert audio to WAV format using pydub
            audio = AudioSegment.from_file(audio_file, format=file_extension.replace('.', ''))
            audio = audio.set_frame_rate(16000).set_channels(1)  # Convert to mono and adjust frame rate
            audio.export("converted_audio.wav", format="wav")

            # Use the converted audio file for recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile("converted_audio.wav") as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language='pt-BR')
                print(text)
                if text.lower() == question_obj.correct_answer.lower():
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