# Generated by Django 4.1.7 on 2024-02-07 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_customuser_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigVariable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True)),
                ('value', models.CharField(blank=True, max_length=32, null=True)),
            ],
        ),
    ]
