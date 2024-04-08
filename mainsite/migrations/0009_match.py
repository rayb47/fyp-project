# Generated by Django 4.2.9 on 2024-04-05 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("mainsite", "0008_alter_word_lesson"),
    ]

    operations = [
        migrations.CreateModel(
            name="Match",
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
                ("left_option", models.CharField(max_length=255)),
                ("right_option", models.CharField(max_length=255)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mainsite.question",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
    ]
