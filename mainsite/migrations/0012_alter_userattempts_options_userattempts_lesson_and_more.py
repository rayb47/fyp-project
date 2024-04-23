# Generated by Django 4.2.9 on 2024-04-08 09:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("mainsite", "0011_usersavedwords"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="userattempts",
            options={"verbose_name_plural": "User Attempts"},
        ),
        migrations.AddField(
            model_name="userattempts",
            name="lesson",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="attempts",
                to="mainsite.lesson",
            ),
        ),
        migrations.AddField(
            model_name="userattempts",
            name="pages_covered",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="userattempts",
            name="questions_answered",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="userattempts",
            name="quiz",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="attempts",
                to="mainsite.quiz",
            ),
        ),
        migrations.AlterField(
            model_name="userattempts",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attempts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="UserAnswers",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("answer_text", models.CharField(max_length=255)),
                ("is_correct", models.BooleanField()),
                ("answer_date", models.DateTimeField(auto_now_add=True)),
                (
                    "attempt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_answers",
                        to="mainsite.userattempts",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_answers",
                        to="mainsite.question",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_answers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "User Answers",
            },
        ),
    ]
