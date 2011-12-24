import re

from django.db.models import Model, DecimalField, DateTimeField, CharField, TextField, ForeignKey
from django.core.validators import RegexValidator
from treebeard.ns_tree import NS_Node

import users.models
import moderation.models
from settings import DEBUG

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
        

class Product(moderation.models.VotingObject):
    name = CharField(max_length=200)
    description = TextField(blank=True)
    cost = DecimalField(max_digits=7, decimal_places=2)
    category = ForeignKey(Category)
    owner = ForeignKey(users.models.Profile)
    date = DateTimeField(auto_now_add=True)
    last_modified = DateTimeField(auto_now=True)

    def is_shadowed(self):
        return self.mark <= 2.5

    def is_hidden(self):
        return self.mark <= 1.5

    def get_high_mark(self):
        return 5

    def get_low_mark(self):
        return 1
    

def get_category_roots():
    return Category.objects.filter(inheritance='')
    
def get_category_leafs():
    return Category.objects.filter(pk__gt=3).extra(where=['''
        ((SELECT COUNT(*) FROM goods_category gc WHERE
        goods_category.inheritance || '.' || goods_category.id = gc.inheritance
        or (goods_category.inheritance = '' and goods_category.id = gc.inheritance)
        )=0)'''])

class Comment(NS_Node, moderation.models.VotingObject):
    product = ForeignKey(Product)
    owner = ForeignKey(users.models.Profile)
    text = TextField()
    time = DateTimeField(auto_now_add=True)

    node_order_by = ['time']

    def iter_depth(self):
        return range(0, self.get_depth())

    def save(self, *args, **kwargs):
        self.time = self.time or datetime.datetime.now()
        return super(Comment, self).save(*args, **kwargs)

    def is_shadowed(self):
        return \
            (self.mark <= 0.5) if DEBUG \
            else (self.vote_set.count() > 5 and self.mark < 0.3)

    def is_hidden(self):
        return (DEBUG or self.vote_set.count() > 5) and self.mark < 0.1

    @property
    def highest_mark(self):
        return 1

    @property
    def lowest_mark(self):
        return 0

    def get_likes(self):
        return self.vote_set.filter(mark=1)
    
    def get_dislikes(self):
        return self.vote_set.filter(mark=0)



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