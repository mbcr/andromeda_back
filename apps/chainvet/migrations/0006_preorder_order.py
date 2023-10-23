# Generated by Django 4.1.7 on 2023-10-22 21:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0008_clientlog'),
        ('chainvet', '0005_assessment_risk_volume_coin_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_type', models.CharField(choices=[('User', 'User'), ('AccessCode', 'AccessCode')], default='User', max_length=10)),
                ('initiated_at', models.DateTimeField(auto_now_add=True)),
                ('last_interaction', models.DateTimeField(auto_now=True, null=True)),
                ('number_of_credits', models.IntegerField(default=0)),
                ('total_price_usd_cents', models.IntegerField(default=0)),
                ('payment_coin', models.CharField(blank=True, max_length=10, null=True)),
                ('payment_network', models.CharField(blank=True, max_length=10, null=True)),
                ('converted_to_order', models.BooleanField(default=False)),
                ('access_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pre_orders', to='users.accesscode')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pre_orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('number_of_credits', models.IntegerField(default=0)),
                ('total_price_usd_cents', models.IntegerField(default=0)),
                ('payment_coin', models.CharField(blank=True, max_length=10, null=True)),
                ('payment_network', models.CharField(blank=True, max_length=10, null=True)),
                ('total_price_crypto', models.FloatField(default=0)),
                ('payment_is_direct', models.BooleanField(default=False)),
                ('payment_address', models.CharField(blank=True, max_length=128, null=True)),
                ('payment_memo', models.CharField(blank=True, max_length=128, null=True)),
                ('swap_details', models.JSONField(blank=True, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('pre_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chainvet.preorder')),
            ],
        ),
    ]