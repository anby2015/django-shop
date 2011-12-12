from django.conf.urls.defaults import patterns, include, url

from cart.views import CartView, CartAddView, CartSetView, CartRemoveView

urlpatterns = patterns('',
	url(r'^$', CartView.as_view()),
	url(r'^add/$', CartAddView.as_view()),
	url(r'^remove/$', CartRemoveView.as_view()),
	url(r'^set/$', CartSetView.as_view()),
)