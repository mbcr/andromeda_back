from django.core.management.base import BaseCommand
from coinpaprika.client import Client
import json
import os
import timeit
from pprint import pprint

from apps.users.models import get_price_in_usd_cents

class Command(BaseCommand):
    help = 'Fetches coins data from Coinpaprika and saves it to a JSON file'

    def handle(self, *args, **kwargs):
        amount_in_usd_cents = get_price_in_usd_cents(12)
        print(f'amount_in_usd_cents: {amount_in_usd_cents}')
        payment_coin = 'xmr-monero'

        start_time = timeit.default_timer()
        free_client = Client()
        # coins_data = free_client.coins()
        conversion_response = free_client.price_converter(base_currency_id='usd-us-dollars', quote_currency_id=payment_coin, amount=amount_in_usd_cents/100)
        pprint(conversion_response)
        amount_in_xmr = conversion_response['price']
        end_time = timeit.default_timer()
        self.stdout.write(self.style.SUCCESS(f'API call duration: {end_time - start_time}'))

        # # Path to save the json file, in the same directory as this script
        # path_to_save = os.path.join(os.path.dirname(__file__), 'paprika_coins.json')

        # with open(path_to_save, 'w') as f:
        #     json.dump(coins_data, f, indent=4)

        self.stdout.write(self.style.SUCCESS(f'Number of coins: {12}. Amount in usd: {amount_in_usd_cents/100}. Amount in XMR: {amount_in_xmr}'))

        self.stdout.write(self.style.SUCCESS(f'Successful'))


    


