# Generated by Django 4.1.7 on 2023-10-21 18:52

import apps.users.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_rename_api_credits_customuser_credits_available_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=16, unique=True)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('credits_paid_for', models.IntegerField(default=0)),
                ('credits_used', models.IntegerField(default=0)),
                ('credits_available', models.IntegerField(default=0)),
            ],
            bases=(models.Model, apps.users.models.CreditOwnerMixin),
        ),
        migrations.AddField(
            model_name='chainvetapikey',
            name='assigned_credits',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='chainvetapikey',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chainvetapikey',
            name='owner_type',
            field=models.CharField(choices=[('User', 'User'), ('AccessCode', 'AccessCode')], default='User', max_length=10),
        ),
        migrations.AddField(
            model_name='chainvetapikey',
            name='reference',
            field=models.CharField(blank=True, max_length=32, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='chainvetapikey',
            name='shares_credits_with_owner',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='credits_paid_for',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='credits_used',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='chainvetapikey',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chainvetapikey',
            name='access_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to='users.accesscode'),
        ),
    ]