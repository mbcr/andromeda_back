# Generated by Django 4.1.7 on 2024-01-20 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_accesscode_affiliate_origin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesscode',
            name='code',
            field=models.CharField(db_index=True, max_length=16, unique=True),
        ),
    ]