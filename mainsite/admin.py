from django.contrib import admin
from .models import Question

# Register your models here.
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'correct_answer')  # Fields to display in the admin list view
    search_fields = ('question_text', 'question_type')  # Fields to search in the admin list view

admin.site.register(Question, QuestionAdmin)