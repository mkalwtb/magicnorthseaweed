"""
Django management command to run the forecast data scheduler.
"""

from django.core.management.base import BaseCommand
from backend.scheduler import main


class Command(BaseCommand):
    help = 'Run the forecast data scheduler'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting forecast data scheduler...')
        )
        try:
            main()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Scheduler stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Scheduler error: {e}')
            )
