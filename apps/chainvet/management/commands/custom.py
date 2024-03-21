from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Q
from django.db import transaction

from pprint import pprint

from apps.chainvet import models
from apps.users import models as user_models


class Command(BaseCommand):
    help = 'Custom management commands for the chainvet app.'
    

    def add_arguments(self, parser):
        parser.add_argument('action', help='Specify the action to perform')
        parser.add_argument('extra_argument_1', nargs='+', help='First argument for the selected action')

    def handle(self, *args, **options):
        if options.get('action') is None:
            # No action argument provided
            self.print_help('manage.py', 'custom')
            return
        
        action = options['action']

        available_actions = {
            'display_liabilities': self.display_liabilities,
            'search': self.search_assessments,
            'show_assessments_without_network': self.show_assessments_without_network,
            'populate_assessment_networks': self.populate_assessment_networks,
        }

        if action not in available_actions:
            self.stdout.write(self.style.ERROR(f'''Action '{action}' not supported. Available actions: {", ".join(available_actions.keys())}'''))
            return
        
        if action == 'search':
            parameter = options['extra_argument_1'][0]
            available_actions[action](parameter)
            return
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

        access_codes_with_paid_orders = user_models.AccessCode.objects.filter(orders__is_paid=True).distinct().order_by('start_date')
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
            self.stdout.write(f'    User {credit_owner} bought {paid_credits:4} credits,used {used_credits:4}. Liability: {available_credits:4}.')
            total_liabilities_credits += available_credits
            total_sold_credits += paid_credits
            total_used_credits += used_credits
        for credit_owner in access_codes_with_paid_orders:
            available_credits = credit_owner.set_credit_cache()
            paid_credits = credit_owner.credits_paid_for
            used_credits = credit_owner.credits_used
            if used_credits:
                last_assessment_date = credit_owner.assessments.order_by('-time_of_request').first().time_of_request
                self.stdout.write(f"    AC {credit_owner} bought {paid_credits:4} credits, used {used_credits:4}. Start date: {credit_owner.start_date.strftime('%Y-%m-%d %H:%M:%S')}. Last check: {last_assessment_date.strftime('%Y-%m-%d %H:%M:%S')}. Liability: {available_credits:4}.")
            else:
                self.stdout.write(f"    AC {credit_owner} bought {paid_credits:4} credits, used {used_credits:4}. Start date: {credit_owner.start_date.strftime('%Y-%m-%d %H:%M:%S')}. Last check: --------N/A--------. Liability: {available_credits:4}.")
            total_liabilities_credits += available_credits
            total_sold_credits += paid_credits
            total_used_credits += used_credits
        self.stdout.write(f'Total sold: {total_sold_credits}.')
        self.stdout.write(f'Total used: {total_used_credits}.')
        self.stdout.write(f'Total liabilities: {total_liabilities_credits} credits, {total_liabilities_credits*60/100:.2f} USD')

    def search_assessments(self, search_term:str):
        '''
        Purpose: Search for assessments by address hash, transaction hash, or access code.
        Args: search_term: str - The search term to look for.
        Result: Prints a list of assessments that match the search term.
        '''
        search_results = models.Assessment.objects.filter(
            Q(address_hash__icontains=search_term) |
            Q(transaction_hash__icontains=search_term) |
            Q(access_code__code__icontains=search_term)
        ).order_by('time_of_request')

        if search_results:
            self.stdout.write(f'Search results for "{search_term}":')
            for result in search_results:
                self.stdout.write(f'****Assessment ID: {result.id}, Date: {result.time_of_request.strftime("%Y-%m-%d %H:%M:%S")}\n    -   -  - --- -  -   -\n    AccessCode: {result.access_code}, Address: {result.address_hash}, T. Hash: {result.transaction_hash}, Risk score: {result.risk_score}, T.Volume coin: {result.transaction_volume_coin}, T.Volume fiat: {result.transaction_volume_fiat}\n    Risk Signals: {result.risk_signals}\n\n\n')
        else:
            self.stdout.write(f'No results found for "{search_term}".')

    def show_assessments_without_network(self):
        '''
        Purpose: Find assessments without a network specified.
        Args: None
        Result: Prints a list of assessments that do not have a network specified.
        '''
        assessments_without_network = models.Assessment.objects.filter(network__isnull=True)
        if assessments_without_network:
            self.stdout.write(f'Assessments without network specified:')
            results = {}
            for assessment in assessments_without_network:
                try: 
                    self.stdout.write(f"****Assessment ID: {assessment.id}, Currency: {assessment.currency}, Token ID: {assessment.response_data.get('data').get('token_id')}")
                    currency_token_id = f"{assessment.currency} - {assessment.response_data.get('data').get('token_id')}"
                except:
                    self.stdout.write(f'****Assessment ID: {assessment.id}, Currency: {assessment.currency}, Token ID: N/A')
                    currency_token_id = f'{assessment.currency}'
                if currency_token_id not in results:
                    results[currency_token_id] = 1
                else:
                    results[currency_token_id] += 1
            self.stdout.write(f'Found {assessments_without_network.count()} assessments without network specified.')
            self.stdout.write(f'Breakdown:')
            for key, value in results.items():
                self.stdout.write(f'    {key}: {value}')
        else:
            self.stdout.write(f'No assessments found without network specified.')

    def populate_assessment_networks(self):
        '''
        Purpose: Populate the network field of assessments based on the currency field.
        Args: None
        Result: Updates the network field of assessments that do not have a network specified.
        '''
        assessments_without_network = models.Assessment.objects.filter(network__isnull=True)

        if not assessments_without_network:
            self.stdout.write(f'No assessments found without network specified.')
            return
        
        for assessment in assessments_without_network:
            if not assessment.response_data.get('data'):
                self.stdout.write(f'Assessment {assessment.id} does not have response data. Currency: {assessment.currency}')
                transfer_function_no_data = {
                    'btc': 'BTC',
                    'dash': 'DASH',
                    'sol': 'SOL',
                    'doge': 'DOGE',
                    'algo': 'ALGO',
                }
                with transaction.atomic():
                    assessment.network = transfer_function_no_data[assessment.currency]
                    assessment.network_populated_by_script = True
                    assessment.save()
                continue
            try: 
                currency_token_id = f"{assessment.currency} - {assessment.response_data.get('data').get('token_id')}"
                transfer_function = {
                    'BTC - None': 'BTC',
                    'ETH - None': 'ETH',
                    'LTC - None': 'LTC',
                    'BTC - 0': 'BTC',
                    'btc - 0': 'BTC',
                    'btc - None': 'BTC',
                    'ETH - 0': 'ETH',
                    'eth - 0': 'ETH',
                    'eth - None': 'ETH',
                    'ltc - None': 'LTC',
                    'ltc - 0': 'LTC',
                    'SOL - 0': 'SOL',
                    'sol - 0': 'SOL',
                    'sol - None': 'SOL',
                    'trx - 0': 'TRX',
                    'usdt - 9': 'TRX',
                    'usdt - 94252': 'ERC20',
                    'matic - 0': 'MATIC',
                    'matic - None': 'MATIC',
                    'MATIC - None': 'MATIC',
                    'trx - 9': 'TRX',
                    'trx - None': 'TRX',
                    'bsc - None': 'BSC',
                    'xrp - None': 'XRP',
                    'xlm - None': 'XLM',
                    'ada - None': 'ADA',
                    'bch - None': 'BCH',
                    'usdt - None': 'USDT',
                    'bnb - None': 'BNB',
                }
                with transaction.atomic():
                    assessment.network = transfer_function[currency_token_id]
                    assessment.network_populated_by_script = True
                    assessment.save()
            except Exception as e:
                self.stdout.write(f'Error updating assessment {assessment.id}. Error: {str(e)}. Currency: {assessment.currency}')
                continue