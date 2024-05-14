from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Q, Sum, Count
from django.db import transaction

from pprint import pprint
from datetime import datetime

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
            'populate_assessment_price': self.populate_assessment_price,
            'company_income': self.company_income,
        }

        if action not in available_actions:
            self.stdout.write(self.style.ERROR(f'''Action '{action}' not supported. Available actions: {", ".join(available_actions.keys())}'''))
            return
        
        if action == 'search':
            parameter = options['extra_argument_1'][0]
            available_actions[action](parameter)
            return
        if action == 'company_income':
            date_string = options['extra_argument_1'][0]
            available_actions[action](date_string)
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

    def populate_assessment_price(self):
        def access_code_has_paid_orders_until_date(access_code, date):
            return access_code.orders.filter(is_paid=True, paid_at__lte=date).exists(), access_code.orders.filter(is_paid=True, paid_at__lte=date).order_by('paid_at')
        def average_usd_price_for_orders(order_queryset):
            total_price_usd_cents = 0
            total_number_of_credits = 0
            for order in order_queryset:
                total_price_usd_cents += order.total_price_usd_cents
                total_number_of_credits += order.number_of_credits
            return round(total_price_usd_cents / total_number_of_credits)
        def price_of_assessment(order_queryset, assessment_number):
            def prepare_price_discovery(order_queryset):
                price_discovery= []
                order_queryset = order_queryset.filter(is_paid=True).order_by('paid_at')
                order_index = 1
                for order in order_queryset:
                    price_per_assessment = round(order.total_price_usd_cents/order.number_of_credits)
                    price_discovery.append((order_index, order.number_of_credits, price_per_assessment))
                    order_index += 1
                return price_discovery
            def find_price_for_assessment(price_discovery, assessment_number):
                credits_to_index_tf = {}
                accummulated_credits = 0
                for index, number_of_credits, price in price_discovery:
                    accummulated_credits += number_of_credits
                    credits_to_index_tf[index] = accummulated_credits

                index_of_assessment = 1
                while index_of_assessment <= len(credits_to_index_tf.keys()):
                    acc_credits = credits_to_index_tf[index_of_assessment]
                    if assessment_number <= acc_credits:
                        return price_discovery[index_of_assessment-1][2]
                    index_of_assessment += 1

            price_discovery = prepare_price_discovery(order_queryset)
            return find_price_for_assessment(price_discovery, assessment_number)
            
        assessments = models.Assessment.objects.filter(is_mock=False).order_by('time_of_request')
        for assessment in assessments:
            assessment_owner = assessment.access_code
            
            if not assessment_owner:
                assessment_owner = assessment.user
            if not assessment_owner:
                self.stdout.write(self.style.ERROR(f'Assessment {assessment.id} does not have an owner.'))
                continue
            
            date_of_assessment = assessment.time_of_request
            access_code_has_orders, orders = access_code_has_paid_orders_until_date(assessment_owner, date_of_assessment)
            
            if not access_code_has_orders:
                self.stdout.write(self.style.ERROR(f'Assessment {assessment.id} owner {assessment_owner} does not have paid orders.'))
                continue
            
            # Update the assessment price
            # if orders.count()>1:
            number_of_prior_assessments = assessment_owner.assessments.filter(time_of_request__lt=date_of_assessment).count()
            number_of_this_assessment = number_of_prior_assessments + 1
            price_of_this_assessment = price_of_assessment(orders, number_of_this_assessment)
            if price_of_this_assessment != assessment.accounting_price_usd_cents:
                self.stdout.write(f'Assessment {assessment.id} has a different price. Current: {assessment.accounting_price_usd_cents}. Calculated: {price_of_this_assessment}. Updating...')
            with transaction.atomic():
                affiliate_commission_share = assessment_owner.affiliate_origin.income_share/10000 if assessment_owner.affiliate_origin else 0
                assessment.accounting_price_usd_cents = price_of_this_assessment
                assessment.accounting_affiliate_commission_usd_cents = round((price_of_this_assessment-80) * affiliate_commission_share)
                assessment.save(update_fields=['accounting_price_usd_cents', 'accounting_affiliate_commission_usd_cents'])
            #     continue
            # else:
            #     average_price_per_assessment = average_usd_price_for_orders(orders)
            #     if average_price_per_assessment != assessment.accounting_price_usd_cents:
            #         self.stdout.write(f'Assessment {assessment.id} has a different price. Current: {assessment.accounting_price_usd_cents}. Calculated: {price_of_this_assessment}. Updating...')
            #     with transaction.atomic():
            #         affiliate_commission_share = assessment_owner.affiliate_origin.income_share/10000 if assessment_owner.affiliate_origin else 0
            #         assessment.accounting_price_usd_cents = average_price_per_assessment
            #         assessment.accounting_affiliate_commission_usd_cents = round((average_price_per_assessment-80) * affiliate_commission_share)
            #         assessment.save(update_fields=['accounting_price_usd_cents', 'accounting_affiliate_commission_usd_cents'])
            
    def company_income(self, date_string:str):
        '''
        Purpose: Assess the profit and loss of the company for a given time-window.
        Args: date_string: str - The time-window to assess the profit and loss for. Format: 'YYYY-MM-DD/YYYY-MM-DD'
        Result: Prints the profit and loss of the company for the given time-window.
        '''
        initial_date, final_date = date_string.split('/')
        initial_date = datetime.strptime(initial_date, '%Y-%m-%d')
        final_date = datetime.strptime(final_date, '%Y-%m-%d')
        
        def assessments_used_by_access_code_until_date(access_code, date)->int:
            return access_code.assessments.filter(time_of_request__lte=date).count()
        def total_revenue_of_access_code_in_time_window(access_code, initial_date, final_date):
            assessments_used_previously = assessments_used_by_access_code_until_date(access_code, initial_date)
            assessments_used_in_time_window = assessments_used_by_access_code_until_date(access_code, final_date) - assessments_used_previously
            if assessments_used_in_time_window == 0:
                return 0

            access_code_has_orders, orders = access_code_has_paid_orders_until_date(access_code, final_date)
            if not access_code_has_orders:
                return 0
            access_code_has_previous_orders, previous_orders = access_code_has_paid_orders_until_date(access_code, initial_date)
            if not access_code_has_previous_orders:
                average_price_per_assessment = average_usd_price_for_orders(orders)
                return assessments_used_in_time_window * average_price_per_assessment
            else:
                total_credits_bought_previously = previous_orders.aggregate(Sum('number_of_credits'))['number_of_credits__sum']
                total_credits_bought_in_time_window = orders.aggregate(Sum('number_of_credits'))['number_of_credits__sum']
                initial_credits_available = total_credits_bought_previously - assessments_used_previously
                if assessments_used_in_time_window < initial_credits_available:
                    pass


        orders_paid = models.Order.objects.filter(is_paid=True, paid_at__gte=initial_date, paid_at__lte=final_date).order_by('paid_at')
        company_sales_usd_cents = 0
        company_sales_credits = 0
        company_deferred_revenue = 0
        company_current_assets = 0
        for order in orders_paid:
            company_sales_credits += order.number_of_credits
            company_sales_usd_cents += order.total_price_usd_cents
            company_current_assets += order.total_price_usd_cents
            company_deferred_revenue += order.total_price_usd_cents


        assessments = models.Assessment.objects.filter(is_mock=False, time_of_request__gte=initial_date, time_of_request__lte=final_date).order_by('time_of_request')
        company_revenue = 0
        company_expenses = 0
        company_commissions = 0
        company_profit = 0
        for assessment in assessments:
            try:
                company_revenue += assessment.accounting_price_usd_cents
                company_deferred_revenue -= assessment.accounting_price_usd_cents
                company_expenses += 60 # Base cost of assessment
                commission = assessment.accounting_affiliate_commission_usd_cents
                if commission < 0:
                    commission = 0
                company_commissions += commission
                company_profit += assessment.accounting_price_usd_cents - 60 - commission
                print(f'Assessment {assessment.id}, AC: {assessment.access_code.code if assessment.access_code else assessment.user.email}, {assessment.time_of_request} Rev: {assessment.accounting_price_usd_cents}, Comm: {commission}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing assessment ID {assessment.id}, AC: {assessment.access_code.code}. Accounting price: {assessment.accounting_price_usd_cents}. Affiliate Commissions: {assessment.accounting_affiliate_commission_usd_cents} Error: {str(e)}.'))

        assets_credits = assessments.last().response_data.get("meta").get("calls_left")
        assets_total = (company_current_assets+assets_credits*60)/100
        liabilities_total = (company_deferred_revenue+company_commissions)/100

        self.stdout.write(f' ')
        self.stdout.write(f'Financial Report for the period {initial_date} to {final_date}')
        self.stdout.write(f' ')
        self.stdout.write(f'Orders processed: {orders_paid.count()} Credits sold: {company_sales_credits}   Credits used: {assessments.count()}   Credit liability changed by: {company_sales_credits - assessments.count()}')
        self.stdout.write(f'--- - - - ---')
        self.stdout.write(f'Company P&L accounts:')
        self.stdout.write(f'    Sales: {company_sales_usd_cents/100:.2f} USD. ({company_sales_credits} credits)')
        self.stdout.write(f'    Revenue: {company_revenue/100} USD. ({assessments.count()} credits)')
        self.stdout.write(f'    COGS: -{company_expenses/100} USD.')
        self.stdout.write(f'    Commissions: -{company_commissions/100} USD.')
        self.stdout.write(f'    Profit: {company_profit/100} USD.')
        self.stdout.write(f'--- - - - ---')
        self.stdout.write(f'Assets and Liability deltas:')
        self.stdout.write(f'    Current assets: {company_current_assets/100} USD.')
        self.stdout.write(f'    AML Credits: {(assets_credits*60)/100} USD. ({assets_credits} credits)')
        self.stdout.write(f'    TOTAL ASSETS: {assets_total} USD.')
        self.stdout.write(f'    ---')
        self.stdout.write(f'    Deferred revenue: {company_deferred_revenue/100} USD.')
        self.stdout.write(f'    Provision for comissions: {company_commissions/100} USD.')
        self.stdout.write(f'    TOTAL LIABILITIES: {liabilities_total} USD.')
        self.stdout.write(f'    ---')
        self.stdout.write(f'    Retained Earnings: {company_profit/100} USD.')
        self.stdout.write(f"    Shareholder's Equity: {3000.00} USD.")
        self.stdout.write(f'    TOTAL EQUITY: {company_profit/100 + 3000} USD.')
        self.stdout.write(f'A-L-E CHECK: {assets_total} - {liabilities_total} - {company_profit/100 + 3000} = {assets_total - liabilities_total - company_profit/100 - 3000:.2f}')

    def check_assessments_with_specific_id(target_id:str):
        assessments = models.Assessment.objects.filter(Q(response_data__id=target_id))
        count = assessments.count()
        print(f'Found {count} assessments with ID {target_id}.')
        for assessment in assessments:
            assessment.status_assessment = 'non-ready'
            assessment.save()
            assessment.update_assessment()
            print(f'    Assessment {assessment.id} updated.')



    self.stdout.write(f'Found {count} assessments with ID {target_id}.')





















