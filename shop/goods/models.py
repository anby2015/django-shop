from django.db import models
from django.db.models import Model, IntegerField, DateField, CharField, TextField, ForeignKey

class Category(Model):
    name = CharField(max_length=50)
    inheritance = TextField() # /\d+(\.\d+)*/
    
    def set_parent(self, c, save=False):
        self.inheritance = '%s.%d' % (c.inheritance, c.pk)
        self.save(commit=save)
    
    def extract_parent(self, c, queryset=None, do_get=True):
        q = queryset or Category.objects.all()
        params = {'pk': self.inheritance.split('.')[-1]}
        return q.get(**params) if do_get else q.filter(**params)[0]
    
    def get_parents_line(self, queryset=None):
        q = queryset or Category.objects.all()
        return q.filter(pk__in=inheritance.split('.'))
    
    def get_dhildren(self, queryset=None):
        q = queryset or Category.objects.all()
        return q.filter(inheritance__regexp=self.inheritance + r'\.\d+')
    

class Product(Model):
    name = CharField(max_length=200)
    description = TextField()
    category = ForeignKey(Category)
