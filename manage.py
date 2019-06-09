#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import schedule
import subprocess
import time
from threading import Thread

def job():
    subprocess.call(cmd,shell=True)

def runscheduler():
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    schedule.every().day.at("23:51").do(job)
    p=Thread(target=runscheduler)
    p.start()
    main()
