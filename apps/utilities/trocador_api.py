import requests
import logging


main_url = 'https://trocador.app/en/'

def get_trade_status(trade_id: str):
    url = main_url + 'anonpay/status/' + trade_id
    response = requests.get(url)
    return response.json()