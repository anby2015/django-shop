import goods.models

def get_category_roots(request):
    return {'root_categories': goods.models.get_category_roots}
