# Generated by Django 4.1.7 on 2024-03-15 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chainvet', '0015_assessment_client_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='is_mock',
            field=models.BooleanField(default=False),
        ),
    ]
