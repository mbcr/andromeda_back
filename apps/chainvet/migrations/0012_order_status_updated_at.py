# Generated by Django 4.1.7 on 2024-01-29 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chainvet', '0011_order_anonpay_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status_updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
