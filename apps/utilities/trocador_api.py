import requests
import logging
from django.utils.timezone import now


main_url = 'https://trocador.app/en/'
logger = logging.getLogger('api_calls_trocador')
error_logger = logging.getLogger('error_logger')

def get_trade_status(trade_id: str):
    start_time = now()
    try:
        url = main_url + 'anonpay/status/' + trade_id
        response = requests.get(url)
        end_time = now()
        duration = (end_time - start_time).total_seconds()
        logger.debug(f"trocador_api>get_trade_status: trade_id: {trade_id}, response_code: {response.status_code}. (Duration: {duration} seconds)")
        return response
    except Exception as e:
        end_time = now()
        duration = (end_time - start_time).total_seconds()
        logger.debug(f"trocador_api>get_trade_status: FAILED to get trade_id: {trade_id}, response_code: {response.status_code}. Raising error. (Duration: {duration} seconds)")
        raise e

def get_trade_status_batch(trade_ids: list):
    from django.conf import settings

    start_time = now()
    try:
        url = main_url + 'anonpay/statusbatch/'
        trade_ids_str = ','.join(trade_ids)
        request_data = {
            'api_key': settings.TROCADOR_API_KEY,
            'trade_ids': trade_ids_str
        }
        response = requests.post(url, json=request_data)
        if response.status_code != 200:
            raise Exception(f"trocador_api>get_trade_status_batch: VCW12 Failed to get response from trocador_api.get_trade_status_batch. Status code was: {response.status_code}. Request was: {request_data}.")
        
        end_time = now()
        duration = (end_time - start_time).total_seconds()
        logger.debug(f"trocador_api>get_trade_status_batch: trade_ids ({len(trade_ids)}): {trade_ids}, response_code: {response.status_code}. (Duration: {duration} seconds)")
        return response
    except Exception as e:
        end_time = now()
        duration = (end_time - start_time).total_seconds()
        error_logger.debug(f"trocador_api>get_trade_status_batch: FAILED to get trade_ids_str: {trade_ids_str}, response_code: {response.status_code}. Duration: {duration} seconds. Error: {e}")
        raise Exception(f"Failed to get response from trocador_api.get_trade_status_batch. Error was: {e}. Request was: {request_data}.")