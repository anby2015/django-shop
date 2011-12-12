import re

from django.db.models import Model, DecimalField, DateTimeField, CharField, TextField, ForeignKey
from django.core.validators import RegexValidator

import users.models

validate_category_slug = RegexValidator(re.compile(r'^[\w.-]+$'), u"Enter a valid 'slug' consisting of letters, numbers, underscores, hyphens or dots.", 'invalid')
validate_category_inheritance = RegexValidator(re.compile(r'^(\d+(.\d+)*)?$'), 'BLABLA MAKE ME RIGHT', 'invalid')

class Category(Model):
    name = CharField(max_length=50)
    slug = CharField(max_length=50, unique=True, validators=[validate_category_slug])

    # validate `inheritance` as /|\d+(\.\d+)*/
    # if it is empty, then the category is root
    # it doesn't contain itself
    inheritance = TextField(validators=[validate_category_inheritance])

    class Meta(object):
        verbose_name_plural = 'Categories'
    
    def depth(self):
        i = self.inheritance
        return len(i.split('.')) if i else 0

    def as_parent(self):
        inheritance, pk = self.inheritance, self.pk
        return '%s.%d' % (inheritance, pk) if inheritance else str(pk)

    def set_parent(self, c, save=False):
        self.inheritance = c.as_parent() if c is not None else ''
        if save:
            self.save()

    def extract_parent(self, queryset=None, do_get=True):
        q = queryset or Category.objects.all()
        k = self.inheritance.split('.')[-1] if self.inheritance else -1
        return q.get(pk=k) if do_get else q.filter(pk=k)

    def qs(self, q, inv):
        q = q or Category.objects.all()
        return q.exclude if inv else q.filter

    def get_parents_line(self, queryset=None, invert=False):
        items = self.inheritance and self.inheritance.split('.')
        return self.qs(queryset, invert)(pk__in=items)

    def get_children(self, queryset=None, invert=False):
        return self.qs(queryset, invert)(
            inheritance=self.as_parent()
        )

    def get_subchildren(self, queryset=None, invert=False):
        return self.qs(queryset, invert)(
            inheritance__startswith=self.as_parent()
        )

    def as_url(self):
        return self.slug or 'id_%d' % self.pk

    def __unicode__(self):
        return self.name
        

class Product(Model):
    name = CharField(max_length=200)
    description = TextField(blank=True)
    cost = DecimalField(max_digits=7, decimal_places=2)
    category = ForeignKey(Category)
    owner = ForeignKey(users.models.Profile)
    date = DateTimeField(auto_now_add=True)
    last_modified = DateTimeField(auto_now=True)
    

def get_category_roots():
    return Category.objects.filter(inheritance='')
    
def get_category_leafs():
    return Category.objects.filter(pk__gt=3).extra(where=['''
        ((SELECT COUNT(*) FROM goods_category gc WHERE
        goods_category.inheritance || '.' || goods_category.id = gc.inheritance
        or (goods_category.inheritance = '' and goods_category.id = gc.inheritance)
        )=0)'''])


class Comment(Model):
    product = ForeignKey(Product)
    parent = ForeignKey('self', default=0)
    owner = ForeignKey(users.models.Profile)
    text = TextField()
    time = DateTimeField(auto_now_add=True)


from django.contrib.admin import site, ModelAdmin
from django.forms.models import ModelForm, ModelChoiceField
class CategoryForm(ModelForm):
    class Meta:
        Model = Category
        fields = ('name', 'slug',)
    parent = ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
    )
    def __init__(self, *args, **kwargs):
        res = super(CategoryForm, self).__init__(
            *args, **kwargs
        )
        instance = getattr(self, 'instance')
        if instance:
            q = Category.objects.exclude(pk=instance.pk)
            p = self.fields['parent']
            p.queryset = self.instance.get_subchildren(q, True)
            inh = instance.extract_parent(do_get=False)
            if inh:
                p.initial = inh[0].pk
        return res

    def save(self, commit=False, *args, **kwargs):
        obj = super(CategoryForm, self).save(commit=False, *args, **kwargs)
        obj.set_parent(self.cleaned_data['parent'])
        if commit:
            obj.save()
        return obj

class CategoryAdmin(ModelAdmin):
    form = CategoryForm

site.register(Category, CategoryAdmin)
site.register(Product)
