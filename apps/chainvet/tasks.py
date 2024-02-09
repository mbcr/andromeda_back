from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta

import time
from django.utils import timezone as django_tz
from django.conf import settings
from apps.utilities import system_messenger

from apps.chainvet import models as chainvet_models

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
        try:
            unpaid_orders_with_anonpay_id = chainvet_models.Order.objects.filter(is_paid=False).exclude(anonpay_id__isnull=True).exclude(anonpay_id='')
            anonpay_ids = list(unpaid_orders_with_anonpay_id.values_list('anonpay_id', flat=True))
        except Exception as e:
            raise Exception("apps.chainvet.tasks.checkpayments.batch_check> Failed to get anonpay_ids from db and prepare list for batch check.")
        try:
            response = trocador_api.get_trade_status_batch(anonpay_ids)
            response_json = response.json()
        except Exception as e:
            raise Exception(f"apps.chainvet.tasks.checkpayments.batch_check> Failed to get response from trocador_api.get_trade_status_batch. Request was: {str(anonpay_ids)}.")
        try:
            #Process the response, extracting each trade status and updating the corresponding order in the db.
            pass
        except Exception as e:
            raise Exception("apps.chainvet.tasks.checkpayments.batch_check> Failed to process the response from trocador_api.get_trade_status_batch.")
        return "Success"

    try:
        return individual_checks()
    except Exception as e:
        error_logger.debug("Error in check_unpaid_orders_for_payments: %s", e)
        return "Failed"
