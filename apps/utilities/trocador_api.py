import requests
import logging


main_url = 'https://trocador.app/en/'
logger = logging.getLogger('api_calls_trocador')
error_logger = logging.getLogger('error_logger')

def get_trade_status(trade_id: str):
    try:
        url = main_url + 'anonpay/status/' + trade_id
        response = requests.get(url)
        logger.debug(f"trocador_api>get_trade_status: trade_id: {trade_id}, response_code: {response.status_code}.")
        return response
    except Exception as e:
        logger.debug(f"trocador_api>get_trade_status: FAILED to get trade_id: {trade_id}, response_code: {response.status_code}. Raising error.")
        raise e