from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import BaseListView

from goods.models import Product, Category

PAGINATE_BY = 24

class BaseProductView(TemplateResponseMixin, BaseListView):
    
    paginate_by = PAGINATE_BY
    category = None
    url = None
    
    def get_context_data(self, **kwargs):
        context = super(BaseProductView, self).get_context_data(**kwargs)
        context.update({
            'products': context['object_list'],
            'url': self.get_url(),
        })
        return context
    
    def get_queryset(self):
        c = self.get_category()
        is_str = isinstance(c, basestring)
        if is_str or c.get_children():
            q = {
                'category__inheritance__startswith':
                    c if is_str else c.as_parent()
            }
        else:
            q = {'category': c}
        return Product.objects.filter(**q).order_by('-date')
        
    def get_category(self):
        if self.category is None:
            c = self.kwargs['category']
            is_id = c.startswith('id_')
            getobj = Category.objects.get
            self.category = getobj(pk=c[3:]) if is_id else getobj(slug=c)
        return self.category
    
    def get_url(self):
        if self.url is None:
            self.url = self.generate_url()
        return self.url

class ProductView(BaseProductView):
    
    template_name = 'goods/categories.html'
    
    def generate_url(self):
        return 'category/%s/' % self.get_category().as_url()
