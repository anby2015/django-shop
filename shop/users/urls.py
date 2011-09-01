from django.conf.urls.defaults import patterns, include, url

from users.views import Login, Logout, Register

urlpatterns = patterns('users.views',
    url(r'^login/$', Login.as_view()),
    url(r'^logout/$', Logout.as_view()),
    url(r'^create/$', Register.as_view()),
)
