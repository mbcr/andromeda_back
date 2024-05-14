from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone as django_tz
from django.conf import settings

from datetime import datetime, timedelta
import time
import logging
import json

from apps.utilities import system_messenger
from apps.chainvet import models as chainvet_models
from apps.utilities import trocador_api
from apps.users.models import ConfigVariable


logger = logging.getLogger('info_logger')
error_logger = get_task_logger('error_logger')

@shared_task(name = "check_unpaid_orders_for_payments")
def check_payments():
    def individual_checks():
        try:
            unpaid_orders = chainvet_models.Order.objects.filter(is_paid=False)
            for unpaid_order in unpaid_orders:
                # minutes_since_last_update = unpaid_order.minutes_since_last_update()
                minutes_since_creation = unpaid_order.minutes_since_created()
                if minutes_since_creation > 30:
                    continue
                last_update = unpaid_order.status_updated_at
                if not last_update:
                    last_update = unpaid_order.created_at
                time_threshold_for_next_check = last_update + timedelta(minutes= (2 + minutes_since_creation/20)) 
                if django_tz.now() > time_threshold_for_next_check:
                    unpaid_order.update_payment_status()
                time.sleep(0.01)
            return "Success"
        except Exception as e:
            raise e

    def batch_check():
        try: # Get a list of all anonpay_ids of unpaid orders from the db
            time_window_update_anonpay_days = int(ConfigVariable.objects.get(name='time_window_update_anonpay_days').value)
            date_cutoff = django_tz.now() - timedelta(days=time_window_update_anonpay_days)
            unpaid_orders_with_anonpay_id = chainvet_models.Order.objects.filter(is_paid=False, created_at__gte=date_cutoff).exclude(anonpay_id__isnull=True).exclude(anonpay_id='')
            anonpay_ids = list(unpaid_orders_with_anonpay_id.values_list('anonpay_id', flat=True))
        except Exception as e:
            raise Exception("apps.chainvet.tasks.checkpayments.batch_check> Failed to get anonpay_ids from db and prepare list for batch check.")
        
        try: # Make a request to the Trocador API
            response = trocador_api.get_trade_status_batch(anonpay_ids)
        except Exception as e:
            error_logger.debug(f"apps.chainvet.tasks.checkpayments.batch_check> Failed to get response from trocador_api.get_trade_status_batch. Error was: {e}.")
            raise Exception(f"apps.chainvet.tasks.checkpayments.batch_check> Failed to get response from trocador_api.get_trade_status_batch. Request was: {str(anonpay_ids)}")
        
        try: # Decode the response    
            response_data = response.json()
        except Exception as e:
            error_logger.debug(f"apps.chainvet.tasks.checkpayments.batch_check> Failed to decode the response from trocador_api.get_trade_status_batch. Error was: {e}. Response was {response.text}.")
            raise Exception(f"apps.chainvet.tasks.checkpayments.batch_check> Failed to decode the response from trocador_api.get_trade_status_batch. Response code was {response.status_code}. Error was: {e}")
        
        try: #Process the response, extracting each trade status and updating the corresponding order in the db.
            trade_objects = response_data.get('status')
            for trade_id in anonpay_ids:
                # Check if any object in the trade_objects list contains the trade_id
                found_trade = next((item for item in trade_objects if item.get('ID') == trade_id), None)
                if found_trade: # If found, update the corresponding order in the db with the object's "Status" value
                    try:
                        target_order = unpaid_orders_with_anonpay_id.filter(anonpay_id=trade_id).first()
                        if not target_order:
                            continue
                        updated_status = found_trade.get('Status')
                        target_order.status = updated_status
                        target_order.status_updated_at = django_tz.now()
                        if updated_status == 'finished':
                            target_order.is_paid = True
                            target_order.paid_at = django_tz.now()
                        target_order.save()
                    except Exception as e:
                        error_logger.debug(f"apps.chainvet.tasks.checkpayments.batch_check> Failed to update order with trade_id: {trade_id}. The status was {updated_status}. Error was: {e}.")
                        continue
                else: # If not found, log the unfound status and time
                    target_order = unpaid_orders_with_anonpay_id.filter(anonpay_id=trade_id).first()
                    if not target_order:
                        continue
                    target_order.status = 'Updating'
                    target_order.status_updated_at = django_tz.now()
                    target_order.save()
        except Exception as e:
            raise Exception(f"apps.chainvet.tasks.checkpayments.batch_check> Failed to process the response from trocador_api.get_trade_status_batch. Error: {e}. Response.json() was : {response_data}")
        return "Success"

    try:
        return batch_check()
    except Exception as e:
        error_logger.debug("Error in check_unpaid_orders_for_payments: %s", e)
        return "Failed"

@shared_task(name = "fetch_missing_trocador_ids")
def fetch_missing_trocador_ids():
    '''
    Fetches the missing anonpay_ids for orders that have been created in the last 3 days. 
    Updates the orders with the fetched anonpay_ids, and trade status
    '''

    # Send request and fetch trade info
    date_cutoff = django_tz.now() - timedelta(days=3)
    missing_anonpay_orders = chainvet_models.Order.objects.filter(anonpay_id__isnull=True, created_at__gte=date_cutoff)
    if not missing_anonpay_orders.exists():
        return "No missing anonpay_ids found within 3 days to be fetched."
    try:
        andromeda_id_list = list(missing_anonpay_orders.values_list('order_id', flat=True))
        response = trocador_api.get_trade_info_for_missing_anonpay_ids(andromeda_id_list)
        response_data = response.json()
    except Exception as e:
        error_logger.debug(f"apps.chainvet.tasks.fetch_missing_trocador_ids> Failed to get or decode response from trocador_api. Error was {str(e)}")
        return "Failed to get or decode response from trocador_api.get_trade_info_for_missing_anonpay_ids."

    # Error handling
    if response.status_code == 204:
        return "No missing anonpay_ids found within 3 days to be fetched."
    if response.status_code != 200:
        error_logger.debug(f"apps.chainvet.tasks.fetch_missing_trocador_ids> Failed to get response from trocador_api. Status code was {response.status_code}. Response was {response.text}.")
        return f"Failed to get response from trocador_api.get_trade_info_for_missing_anonpay_ids. Status code was {response.status_code}. Response was {response.text}."
    
    # Process the response and update the orders
    try:
        for order in missing_anonpay_orders:
            order_id = order.order_id
            if order_id not in response_data:
                continue
            logger.debug(f"apps.chainvet.tasks.fetch_missing_trocador_ids> Order {order_id} found without anonpay_id. Updating...")
            trade_info = response_data[order_id]
            order.anonpay_id = trade_info.get('anonpay_id')
            order.status = trade_info.get('status')
            order.status_updated_at = django_tz.now()
            if trade_info.get('status') == 'finished':
                order.is_paid = True
                order.paid_at = trade_info.get('trade_finished_in')
            order.save()
        return "Success"
    except Exception as e:
        error_logger.debug(f"apps.chainvet.tasks.fetch_missing_trocador_ids> Failed to update orders with fetched anonpay_ids. Error was {str(e)}")
        return "Failed to update orders with fetched anonpay_ids."


@shared_task(name = "update_non_ready_assessments")
def update_non_ready_assessments():
    non_ready_assessments = chainvet_models.Assessment.objects.all().exclude(status_assessment='ready')
    if not non_ready_assessments.exists():
        return "No non-ready assessments found."
    try:
        update_errors = []
        for assessment in non_ready_assessments[:20]:
            try:
                assessment.update_assessment()
            except Exception as e:
                update_errors.append({
                    'assessment_id': assessment.assessment_id,
                    'error': str(e)
                })
        if update_errors:
            error_logger.debug("apps.chainvet.tasks.update_non_ready_assessments> Errors in updating assessments: %s", update_errors)
            return f"Errors occurred: {update_errors}"
    except Exception as e:
        error_logger.debug("apps.chainvet.tasks.update_non_ready_assessments> Error in updating non ready assessments: %s", str(e))
    return "All non-ready assessments updated successfully."