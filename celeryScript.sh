source ../venv/bin/activate
celery -A mysite worker --loglevel=INFO --concurrency=2
