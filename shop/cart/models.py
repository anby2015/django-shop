from django.db.models import (
    Model, OneToOneField, ForeignKey, FloatField,
    ManyToManyField, TextField, PositiveIntegerField,
    Sum, F,
)
from django.db import transaction

from users.models import Profile, EMPTY
from users.fields import CountryField
from goods.models import Product

class Storage(Model):
    products = ManyToManyField(Product, through='StorageItem')

    @property
    def total_sum(self):
        return self.storageitem_set.only('count').select_related('product__cost').extra(
            select={
                'ss':'SUM(cost*count)'
            }
        )[:1][0].ss


class StorageItem(Model):
    product = ForeignKey(Product)
    storage = ForeignKey(Storage)
    count = PositiveIntegerField(default=0)


class Order(Storage):
    assignee = ForeignKey(Profile)
    country = CountryField(**EMPTY)
    city = TextField(**EMPTY)
    address = TextField(**EMPTY)
    payment = FloatField()

REFERRER_COST_MULTIPLIER = 0.15

class Cart(Storage):
    assignee = OneToOneField(Profile)

    def order(self, country=None, city=None, address=None):
        a = self.assignee
        
        total = self.total_sum
        print "TOTAL! " + str(total)

        a.add_fee(float(total) * REFERRER_COST_MULTIPLIER)

        a.fee -= self.discount(total)

        country, city, address = (
            country or a.country,
            city or a.city,
            address or a.get_full_address(),
        )
        with transaction.commit_on_success():
            a.save()
            o = Order.objects.create(
                assignee=a,
                country=country,
                city=city,
                address=address,
                payment=self.payment(total),
            )
            StorageItem.objects.filter(storage=self).update(storage=o)
        self.delete()

    def discount(self, total_sum=None):
        t = total_sum or self.total_sum
        return min(t, self.assignee.fee)
    
    def payment(self, total_sum=None):
        t = total_sum or self.total_sum
        return t - self.discount(t)
