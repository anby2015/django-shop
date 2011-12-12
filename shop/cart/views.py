from django.views.generic.base import View, TemplateResponseMixin, TemplateView
from django.http import HttpResponseRedirect

from cart.models import Cart, StorageItem
from goods.models import Product
from main.class_decorators import login_required
from users.views import get_redirect_url

def get_storage(user, product_id):
	cart, created = Cart.objects.get_or_create(user=user)
	product = Product.objects.get(pk=product_id)
	storage, created = StorageItem.objects.get_or_create(
		storage=cart,
		product=product
	)
	return (cart, storage,)


class PostAndReturnView(View):
	redirect_url = 'redirect_to'

	def post(self, request):
		self.request = request
		try:
			result = self.make_changes()
		finally:
			return HttpResponseRedirect(get_redirect_url(request, self.redirect_url))


@login_required
class CartAddView(PostAndReturnView):
	def make_changes(self):
		get = self.request.POST.get
		cart, storage = get_storage(self.request.user, get('product_id'))
		storage.count += get('count')


@login_required
class CartRemoveView(PostAndReturnView):
	def make_changes(self):
		get = self.request.POST.get
		cart, storage = get_storage(self.request.user, get('product_id'))
		storage.delete()


@login_required
class CartSetView(PostAndReturnView):
	def make_changes(self):
		get = self.request.POST.get
		cart, storage = get_storage(self.request.user, get('product_id'))
		storage.count = get('count')


@login_required
class CartView(TemplateView):
	template_name = 'cart/index.html'

	def get_context_data(self, **kwargs):
		ctx = {}
		try:
			cart = Cart.objects.get(user=self.request.user)
			ctx['products'] = cart.products
		finally:
			return ctx