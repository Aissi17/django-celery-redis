from django.db import models

# Create your models here.


class SalesForecast(models.Model):
    product_name = models.CharField(max_length=120, null=True, blank=True)
    sales_value = models.IntegerField()
    price_value = models.FloatField()

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{product_name}".format(product_name=self.product_name)
