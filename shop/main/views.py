from goods.views import BaseProductView

class Home(BaseProductView):
    
    template_name = 'index.html'
    url = '/home/'
    category = ''
