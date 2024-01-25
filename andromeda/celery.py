# from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')

app = Celery('andromeda')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))



app.conf.beat_schedule = {
    # #Scheduler Name
    # 'telegram-dispatcher-fetch': {
    #     # Task Name (Name Specified in Decorator)
    #     'task': 'telegram_dispatcher_fetch',  
    #     # Schedule      
    #     'schedule': 5.0,
    #     # Function Arguments 
    #     # 'args': ("Hello",) 
    # },
}  

