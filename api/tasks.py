import random
from celery import shared_task
import time
from .models import SalesForecast
import logging
from celery_progress.backend import ProgressRecorder


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    total = x * (y * random.randint(3, 100))
    return total


@shared_task(bind=True)
def go_to_sleep(self, duration):
    progress_recorder = ProgressRecorder(self)
    for i in range(5):
        time.sleep(duration)
        progress_recorder.set_progress(i + 1, 5, f"on iteration {i}")
    time.sleep(duration)
    return "Done"


@shared_task
def get_sf_data(sku):
    logging.warning('The task "SF" is running !')
    time.sleep(5)

    obj = SalesForecast.objects.create(
        product_name=sku,
        sales_value=random.randint(0, 200),
        price_value=random.uniform(0, 1000),
    )

    logging.info("Task finished")
    return sku
