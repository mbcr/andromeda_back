# Generated by Django 4.1.7 on 2023-05-28 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chainvet', '0004_assessment_address_hash_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='risk_volume_coin',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assessment',
            name='risk_volume_fiat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assessment',
            name='transaction_volume_coin',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assessment',
            name='transaction_volume_fiat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assessment',
            name='transaction_volume_fiat_currency_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
