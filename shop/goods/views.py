from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.http import HttpResponseRedirect

from goods.models import Product, Category, Comment
from main.class_decorators import login_required

PAGINATE_BY = 24

class BaseCategoryView(TemplateResponseMixin, BaseListView):
    
    paginate_by = PAGINATE_BY
    category = None
    url = None
    
    def get_context_data(self, **kwargs):
        context = super(BaseCategoryView, self).get_context_data(**kwargs)
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

class CategoryView(BaseCategoryView):
    
    template_name = 'goods/categories.html'
    
    def generate_url(self):
        return '/categories/%s/' % self.get_category().as_url()
    
    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context.update({
            'category': self.get_category()
        })
        return context
    
class ProductView(TemplateResponseMixin, BaseDetailView):
    
    model = Product
    template_name = 'goods/product.html'
    
    def get_context_data(self, **kwargs):
        product = self.kwargs['pk'];
        return {
            'product': self.object,
            'comments': Comment.objects.filter(
                owner=self.request.user.profile,
                product__id=product
            ).order_by('time'),
        }


@login_required
class AddCommentView(View):
    http_method_names = ['post']

    def post(self, request, product_id):
        text = request.POST.get('text')
        if text:
            Comment.objects.create(
                owner=self.request.user.profile,
                product_id=product_id,
                text=text
            )

        return HttpResponseRedirect('../')