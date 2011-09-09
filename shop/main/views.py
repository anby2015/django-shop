from django.shortcuts import render
from django.http import Http404
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import BaseListView

from goods.models import Category, Product, get_category_roots

PAGINATE_BY = 24

def paginate(q, page, from_one=True):
    start = PAGINATE_BY * (page - int(bool(from_one)))
    if start > len(q):
        raise Http404('The page is empty')
    return q[start:][:PAGINATE_BY]

class CategoryView(TemplateResponseMixin, BaseListView):
    
    paginate_by = PAGINATE_BY
    
    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context.update({'products': context['object_list'], 'url': self.url,})
        return context
    

class Home(CategoryView):
    
    template_name = 'index.html'
    url = '/home/'
    
    def get_queryset(self):
        return Product.objects.order_by('-date')
