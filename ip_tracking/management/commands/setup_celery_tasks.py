from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):
    help = 'Set up Celery periodic tasks for anomaly detection'

    def handle(self, *args, **options):
        # Create hourly schedule for anomaly detection
        hourly_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,  # Run at the top of every hour
            hour='*',  # Every hour
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created hourly schedule for anomaly detection')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Hourly schedule already exists')
            )
        
        # Create anomaly detection task
        anomaly_task, created = PeriodicTask.objects.get_or_create(
            name='Detect Suspicious IPs',
            defaults={
                'task': 'ip_tracking.tasks.detect_suspicious_ips',
                'crontab': hourly_schedule,
                'enabled': True,
                'kwargs': json.dumps({}),
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created anomaly detection task')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Anomaly detection task already exists')
            )
        
        # Create cleanup task (run every 6 hours)
        cleanup_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour='*/6',  # Every 6 hours
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created cleanup schedule')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Cleanup schedule already exists')
            )
        
        # Create cleanup task
        cleanup_task, created = PeriodicTask.objects.get_or_create(
            name='Cleanup Old Suspicious IPs',
            defaults={
                'task': 'ip_tracking.tasks.cleanup_old_suspicious_ips',
                'crontab': cleanup_schedule,
                'enabled': True,
                'kwargs': json.dumps({}),
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created cleanup task')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Cleanup task already exists')
            )
        
        # Create daily security report task
        daily_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=0,  # Midnight
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created daily schedule')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Daily schedule already exists')
            )
        
        # Create security report task
        report_task, created = PeriodicTask.objects.get_or_create(
            name='Generate Security Report',
            defaults={
                'task': 'ip_tracking.tasks.generate_security_report',
                'crontab': daily_schedule,
                'enabled': True,
                'kwargs': json.dumps({}),
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created security report task')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Security report task already exists')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Celery periodic tasks setup completed!')
        )
        self.stdout.write(
            'Make sure to run: celery -A alx_backend_security beat --loglevel=info'
        )
