from django.conf.urls.defaults import patterns, include, url
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html")),
)
