from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from users.views import CompleteRegistration
from goods.urls import category_patterns, products_patterns
from goods.views import FullTreeView

# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shop.views.home', name='home'),
    # url(r'^shop/', include('shop.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', RedirectView.as_view(url='/home/')),
    url(r'^home/', include('main.urls')),
    
    url(r'^categories/', include(category_patterns)),
    url(r'^products/', include(products_patterns)),
        
    url(r'^users/', include('users.urls')),
    url(r'^thanks/', CompleteRegistration.as_view()),

    url(r'^cart/', include('cart.urls')),

    url(r'^tree/$', FullTreeView.as_view()),

    url(r'^ref/', include('referrals.urls')),
    
    url(
        r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}
    ),
)
