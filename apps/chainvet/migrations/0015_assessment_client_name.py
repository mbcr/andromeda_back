# Generated by Django 4.1.7 on 2024-02-29 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chainvet', '0014_assessment_cbc_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='client_name',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]
