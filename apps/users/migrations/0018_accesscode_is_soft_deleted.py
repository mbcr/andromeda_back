# Generated by Django 4.1.7 on 2024-03-22 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_affiliate_income_share'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesscode',
            name='is_soft_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
