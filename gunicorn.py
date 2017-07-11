import multiprocessing
import os

bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8080')
workers = os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)
worker_class = os.environ.get('GUNICORN_WORKER', 'gevent')
accesslog = '/dev/null'
errorlog = '-'
