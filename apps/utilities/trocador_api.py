import requests
import logging


main_url = 'https://trocador.app/en/'
logger = logging.getLogger('api_calls_trocador')

def get_trade_status(trade_id: str):
    url = main_url + 'anonpay/status/' + trade_id
    response = requests.get(url)
    logger.debug(f"trocador_api>get_trade_status: trade_id: {trade_id}, response_code: {response.status_code}")
    return response.json()