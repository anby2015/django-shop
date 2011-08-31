from django.conf.urls.defaults import patterns, include, url

import users.views

urlpatterns = patterns('users.views',
    url(r'^login/$', users.views.Login.as_view()),
    url(r'^logout/$', users.views.Logout.as_view()),
    url(r'^create/$', users.views.Register.as_view()),
)
