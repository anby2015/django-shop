from django.conf.urls.defaults import patterns, include, url

from goods.views import CategoryView

category_patterns = patterns('',
    url(r'^(?P<category>[\w.-]+)/$', CategoryView.as_view(), {'page': 1}),
    url(r'^(?P<category>[\w.-]+)/(?P<page>\d+)/$', CategoryView.as_view()),
)
