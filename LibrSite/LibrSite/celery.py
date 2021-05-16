import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
# this is also used in manage.pyc
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibrSite.settings')

app = Celery('LibrSite')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_create_missing_queues = True
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.broker_url = 'redis://77.47.204.199:6379/5'
app.conf.result_backend = 'redis://77.47.204.199:6379/6'

app.conf.task_routes = ([
    ('send_mail', {'queue': 'mail'}),
    ('update_ratings', {'queue': 'long'}),
],)

app.conf.beat_schedule = {
    'update_books_scheduled': {
        'task': 'update_ratings',
        'schedule': 60.0,   # 7200 = 2 hours,  another value is for test
    },
}

