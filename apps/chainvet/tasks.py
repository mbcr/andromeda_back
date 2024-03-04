from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone as django_tz
from django.conf import settings

from datetime import datetime, timedelta
import time
import logging

from apps.utilities import system_messenger
from apps.chainvet import models as chainvet_models
from apps.utilities import trocador_api
from apps.users.models import ConfigVariable

error_logger = get_task_logger('error_logger')

logger = logging.getLogger('info_logger')

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
        try: # Make a request to the API and decode the json response
            response = trocador_api.get_trade_status_batch(anonpay_ids)
            response_data = response.json()
        except Exception as e:
            raise Exception(f"apps.chainvet.tasks.checkpayments.batch_check> Failed to get response from trocador_api.get_trade_status_batch. Request was: {str(anonpay_ids)}.")
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
            raise Exception("apps.chainvet.tasks.checkpayments.batch_check> Failed to process the response from trocador_api.get_trade_status_batch.")
        return "Success"

    try:
        return batch_check()
    except Exception as e:
        error_logger.debug("Error in check_unpaid_orders_for_payments: %s", e)
        return "Failed"


@shared_task(name = "update_non_ready_assessments")
def check_payments():
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