from django.db.models import Model, DecimalField, DateTimeField, CharField, TextField, ForeignKey

import users.models

class Category(Model):
    name = CharField(max_length=50)
    slug = CharField(max_length=50, unique=True) # validate as /[\w.-]*/
    
    # validate `inheritance` as /|\d+(\.\d+)*/
    # if it is empty, then the category is root
    # it doesn't contain itself
    inheritance = TextField()
    
    def as_parent(self):
        inheritance, pk = self.inheritance, self.pk
        return '%s.%d' % (inheritance, pk) if inheritance else str(pk)
    
    def set_parent(self, c, save=False):
        self.inheritance = c.as_parent() if c is not None else ''
        if save:
            self.save()
    
    def extract_parent(self, c, queryset=None, do_get=True):
        q = queryset or Category.objects.all()
        params = {'pk': self.inheritance.split('.')[-1]}
        return q.get(**params) if do_get else q.filter(**params)[0]
    
    def get_parents_line(self, queryset=None):
        q = queryset or Category.objects.all()
        return q.filter(pk__in=inheritance.split('.'))
    
    def get_children(self, queryset=None):
        q = queryset or Category.objects.all()
        return q.filter(inheritance=self.as_parent())
       
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
    
from django.contrib.admin import site, ModelAdmin
from django.forms.models import ModelForm, ModelChoiceField
class CategoryForm(ModelForm):
    class Meta:
        fields = ('name', 'slug',)
        Model = Category
    parent = ModelChoiceField(queryset=Category.objects.all(), required=False)
    def save(self, commit=False, *args, **kwargs):
        obj = super(CategoryForm, self).save(commit=    False, *args, **kwargs)
        obj.set_parent(self.cleaned_data['parent'])
        if commit:
            obj.save()
        return obj
class CategoryAdmin(ModelAdmin):
    form = CategoryForm
site.register(Category, CategoryAdmin)
site.register(Product)
