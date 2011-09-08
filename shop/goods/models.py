from django.db import models
from django.db.models import Model, IntegerField, DateField, CharField, TextField, ForeignKey

class Category(Model):
    name = CharField(max_length=50)
    
    # validate `inheritance` as /|\d+(\.\d+)*/
    # if it is empty, then the category is root
    # it doesn't contain itself
    inheritance = TextField()
    
    def as_parent(self):
        inheritance, pk = self.inheritance, self.pk
        return '%s.%d' % (inheritance, pk) if inheritance else str(pk)
    
    def set_parent(self, c, save=False):
        self.inheritance = c.as_parent()
        if save:
            self.save()
    
    def extract_parent(self, c, queryset=None, do_get=True):
        q = queryset or Category.objects.all()
        params = {'pk': self.inheritance.split('.')[-1]}
        return q.get(**params) if do_get else q.filter(**params)[0]
    
    def get_parents_line(self, queryset=None):
        q = queryset or Category.objects.all()
        return q.filter(pk__in=inheritance.split('.'))
    
    def get_dhildren(self, queryset=None):
        q = queryset or Category.objects.all()
        return q.filter(inheritance=self.as_parent())
       
    def as_slug(self):
        return str(self.pk)
    

class Product(Model):
    name = CharField(max_length=200)
    description = TextField()
    category = ForeignKey(Category)
    

def get_category_roots():
    return Category.objects.filter(inheritance='')
