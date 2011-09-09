from django.conf.urls.defaults import patterns, include, url

from goods.views import ProductView

category_patterns = patterns('',
    url(r'(?P<category>.+)/$', ProductView.as_view(), {'page': 1}),
    url(r'(?P<category>.+)/(?P<page>\d+)/$', ProductView.as_view()),
)
