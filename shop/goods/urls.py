from django.conf.urls.defaults import patterns, include, url

from goods.views import CategoryView, ProductView, AddCommentView, CommentVoteView

category_patterns = patterns('',
    url(r'^(?P<category>[\w.-]+)/$', CategoryView.as_view(), {'page': 1}),
    url(r'^(?P<category>[\w.-]+)/(?P<page>\d+|last)/$', CategoryView.as_view()),
)

products_patterns = patterns('',
    url(r'^(?P<pk>\d+)/$', ProductView.as_view()),
    url(r'^(?P<product_id>\d+)/add_comment/$', AddCommentView.as_view()),
    url(r'^(?P<product_id>\d+)/like_(?P<cid>\d+)/$', CommentVoteView.as_view(), {'mark': 1}),
    url(r'^(?P<product_id>\d+)/dislike_(?P<cid>\d+)/$', CommentVoteView.as_view(), {'mark': 0}),
)
