# Generated by Django 4.1.7 on 2023-10-22 21:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logManager', '0002_landingpagepipelinelog_url'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LandingPagePipelineLog',
            new_name='AccessLog',
        ),
    ]