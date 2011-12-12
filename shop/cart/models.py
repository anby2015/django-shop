from django.db.models import Model, OneToOneField, ForeignKey, ManyToManyField, TextField, PositiveIntegerField
from django.db import transaction

from users.models import Profile
from goods.models import Product

class Storage(Model):
    products = ManyToManyField(Product, through='StorageItem')


class StorageItem(Model):
    product = ForeignKey(Product)
    storage = ForeignKey(Storage)
    count = PositiveIntegerField(default=0)


class Order(Storage):
    assignee = ForeignKey(Profile)
    address = TextField()


class Cart(Storage):
    assignee = OneToOneField(Profile)

    def order(self, address=None):
        a = self.assignee
        address = address or a.get_full_address()
        with transaction.commit_on_success():
            o = Order.objects.create(
                assignee=a,
                products=self.products,
                address=address,
            )
            self.delete()