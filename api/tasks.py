import random
from celery import shared_task
import time
from .models import SalesForecast


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    total = x * (y * random.randint(3, 100))
    return total


@shared_task
def get_sf_data(sku):
    time.sleep(5)

    obj = SalesForecast.objects.create(
        product_name=sku,
        sales_value=random.randint(0, 200),
        price_value=random.uniform(0, 1000),
    )

    return sku
