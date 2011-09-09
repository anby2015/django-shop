from goods.views import BaseCategoryView

class Home(BaseCategoryView):
    
    template_name = 'index.html'
    url = '/home/'
    category = ''
