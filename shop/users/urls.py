from django.conf.urls.defaults import patterns, include, url
from users.views import Login

urlpatterns = patterns('users.views',
    url(r'^login/$', Login.as_view()),
    url(r'^logout/$', 'logout'),
    
)
