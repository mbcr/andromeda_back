# Generated by Django 4.1.7 on 2024-04-01 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chainvet', '0019_assessment_accounting_crypto_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='accounting_affiliate_commission_usd_cents',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
