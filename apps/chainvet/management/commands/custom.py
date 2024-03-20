from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pprint import pprint

from apps.chainvet import models
from apps.users import models as user_models


class Command(BaseCommand):
    help = 'Custom management commands for the chainvet app.'
    

    def add_arguments(self, parser):
        parser.add_argument('action', help='Specify the action to perform')
        # parser.add_argument('extra_argument_1', nargs='+', help='First argument for the selected action')

    def handle(self, *args, **options):
        if options.get('action') is None:
            # No action argument provided
            self.print_help('manage.py', 'custom')
            return
        
        action = options['action']

        available_actions = {
            'display_liabilities': self.display_liabilities,
        }

        if action not in available_actions:
            self.stdout.write(self.style.ERROR(f'''Action '{action}' not supported. Available actions: {", ".join(available_actions.keys())}'''))
            return
        
        # if action == 'action_name_requiring_argument':
        #     parameter = options['extra_argument_1'][0]
        #     available_actions[action](parameter)
        #     return
        available_actions[action]()

    def display_liabilities(self):
        """
        Purpose: Finds all current liabilities - paid but unused credits.
        Args: None
        Result: Prints a totalling of all liabilities, as well as a list of each access code and the amount of unused credits it has.
        """

        users_with_paid_orders = user_models.CustomUser.objects.filter(orders__is_paid=True).distinct()
        user_emails_to_ignore = ['mail@trocador.app']
        users_with_paid_orders = users_with_paid_orders.exclude(email__in=user_emails_to_ignore)

        access_codes_with_paid_orders = user_models.AccessCode.objects.filter(orders__is_paid=True).distinct()
        access_codes_to_ignore = ['5VWDtKVYmX9jgBAv', 'yVQqqEVPt2OFEkbG', 'k7os7vGY3W6nYfoS'] # Trocador main access code and test accounts
        access_codes_with_paid_orders = access_codes_with_paid_orders.exclude(code__in=access_codes_to_ignore)

        total_liabilities_credits = 0
        total_sold_credits = 0
        total_used_credits = 0

        self.stdout.write(f'Current liability list:')
        for credit_owner in users_with_paid_orders:
            available_credits = credit_owner.set_credit_cache()
            paid_credits = credit_owner.credits_paid_for
            used_credits = credit_owner.credits_used
            self.stdout.write(f'    User {credit_owner} has bought {paid_credits} credits, and used {used_credits} of them. Liability: {available_credits}.')
            total_liabilities_credits += available_credits
            total_sold_credits += paid_credits
            total_used_credits += used_credits
        for credit_owner in access_codes_with_paid_orders:
            available_credits = credit_owner.set_credit_cache()
            paid_credits = credit_owner.credits_paid_for
            used_credits = credit_owner.credits_used
            self.stdout.write(f'    Access Code {credit_owner} has bought {paid_credits} credits, and used {used_credits} of them. Start date: {credit_owner.start_date} Liability: {available_credits}.')
            total_liabilities_credits += available_credits
            total_sold_credits += paid_credits
            total_used_credits += used_credits
        self.stdout.write(f'Total sold: {total_sold_credits}.')
        self.stdout.write(f'Total used: {total_used_credits}.')
        self.stdout.write(f'Total liabilities: {total_liabilities_credits} credits, {total_liabilities_credits*60/100:.2f} USD')

    


