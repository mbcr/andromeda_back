# Generated by Django 4.1.7 on 2024-03-20 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chainvet', '0016_assessment_is_mock'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='network',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
