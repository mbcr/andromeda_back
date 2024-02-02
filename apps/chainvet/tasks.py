from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta

import time
from django.utils import timezone as django_tz
from django.conf import settings
from apps.utilities import system_messenger

from apps.chainvet import models as chainvet_models

logger = get_task_logger(__name__)


@shared_task(name = "check_unpaid_orders_for_payments")
def check_payments():
    try:
        unpaid_orders = chainvet_models.Order.objects.filter(is_paid=False)
        for unpaid_order in unpaid_orders:
            # minutes_since_last_update = unpaid_order.minutes_since_last_update()
            minutes_since_creation = unpaid_order.minutes_since_created()
            last_update = unpaid_order.status_updated_at
            if not last_update:
                last_update = unpaid_order.created_at
            time_threshold_for_next_check = last_update + timedelta(minutes= 2) + minutes_since_creation/20
            if django_tz.now() > time_threshold_for_next_check:
                unpaid_order.update_payment_status()
            time.sleep(0.05)

    except Exception as e:
        logger.exception("Error in fetch_messages: %s", e)
        return "Failed"
