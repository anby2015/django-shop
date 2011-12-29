from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('referrals.views',
	(r'^userinvite/(?P<username>[\w]+)/(?P<product_id>\d+)/$', 'ref_redirect',),
)