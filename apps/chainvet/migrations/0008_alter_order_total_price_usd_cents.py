# Generated by Django 4.1.7 on 2023-10-27 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chainvet', '0007_assessment_access_code_alter_assessment_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price_usd_cents',
            field=models.FloatField(default=0),
        ),
    ]