from django.conf.urls.defaults import patterns, include, url
from django.views.generic.base import RedirectView

from main.views import Home

urlpatterns = patterns('',
    url(r'^$', Home.as_view(), {'page': 1}),
    url(r'^(?P<page>\d+|last)/$', Home.as_view()),
)
