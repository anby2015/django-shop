from djnago.shortcuts import render

from goods.models import Category, Product, get_category_roots

PAGINATE_BY = 50

def get_page(q, page_num, from_one=True):
    return q[PAGINATE_BY * (page_num - (1 if from_one else 0)) : PAGINATE_BY]

def index(request, page=1):
    context = {
        'in_root': True,
        'categories': get_category_roots(),
        'products': get_page(Product.objects.order_by('-date'), page)
    }
    return render(request, 'index.html', context)
