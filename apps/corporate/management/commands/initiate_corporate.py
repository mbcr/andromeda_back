from django.core.management.base import BaseCommand, CommandError

from pprint import pprint

from apps.corporate import models as corporate_models


class Command(BaseCommand):
    help = 'Command to initiate the database models for the corporate app.'

    def handle(self, *args, **options):
        # Create the Account instances
        def create_new_account_instance(name, category):
            new_instance, created = corporate_models.Account.objects.get_or_create(name=name, category=category)
            if not created:
                self.stdout.write(self.style.WARNING(f'Account: {name:>20} ({category}) already exists.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Account: {name:>20} ({category}) created successfully.'))
        
        create_new_account_instance('XMR', 'Assets')
        create_new_account_instance('USDT', 'Assets')
        create_new_account_instance('CBC Credit', 'Assets')
        create_new_account_instance('Dividend Payment', 'Equity')