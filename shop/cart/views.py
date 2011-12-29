from django.views.generic.base import View, TemplateResponseMixin, TemplateView
from django.http import HttpResponseRedirect, HttpResponse

from cart.models import Cart, StorageItem
from goods.models import Product
from goods.views import PostAndReturnView
from main.class_decorators import login_required

def get_storage(user, product_id):
	cart, created = Cart.objects.get_or_create(assignee=user.profile)
	product = Product.objects.get(pk=product_id)
	storage, created = StorageItem.objects.get_or_create(
		storage=cart,
		product=product
	)
	return (cart, storage,)


@login_required
class CartAddView(PostAndReturnView):
	def make_changes(self):
		get = self.request.POST.get
		cart, storage = get_storage(self.request.user, get('product_id'))
		storage.count += int(get('count'))
		storage.save()


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
		storage.count = int(get('count'))
		storage.save()


@login_required
class CartView(TemplateView):
	template_name = 'cart/index.html'

	def get_context_data(self, **kwargs):
		ctx = {}
		try:
			cart = Cart.objects.get(assignee=self.request.user)
			ctx['products'] = cart.storageitem_set
			ctx['cart'] = cart
		finally:
			return ctx

@login_required
class CartOrderView(PostAndReturnView):
	def make_changes(self):
		cart = Cart.objects.get(assignee=self.request.user.profile)
		cart.order()