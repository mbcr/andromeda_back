# Generated by Django 4.1.7 on 2023-10-22 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logManager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='landingpagepipelinelog',
            name='url',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
