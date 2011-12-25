import datetime

from django.views.generic.base import View, TemplateResponseMixin, TemplateView
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.http import HttpResponseRedirect
from django.db.models import F, Avg

from goods.models import Product, Category, Comment
from main.class_decorators import login_required, unbanned_only
from users.views import get_redirect_url
from moderation.models import Vote

PAGINATE_BY = 24

class PostAndReturnView(View):
    redirect_url = 'redirect_to'

    def post(self, request):
        self.request = request
        try:
            result = self.make_changes()
        except Exception as e:
            print "BEEEEEEEEEEEEEEEEEEP!" + str(e)
        finally:
            return HttpResponseRedirect(get_redirect_url(request, self.redirect_url))


class BaseCategoryView(TemplateResponseMixin, BaseListView):
    
    paginate_by = PAGINATE_BY
    category = None
    url = None

    def get_context_data(self, **kwargs):
        context = super(BaseCategoryView, self).get_context_data(**kwargs)
        context.update({
            'products': context['object_list'],
            'url': self.get_url(),
        })
        return context
    
    def get_queryset(self):
        c = self.get_category()
        is_str = isinstance(c, basestring)
        if is_str or c.get_children():
            q = {
                'category__inheritance__startswith':
                    c if is_str else c.as_parent()
            }
        else:
            q = {'category': c}
        return Product.objects.filter(**q).order_by('-date')
        
    def get_category(self):
        if self.category is None:
            c = self.kwargs['category']
            is_id = c.startswith('id_')
            getobj = Category.objects.get
            self.category = getobj(pk=c[3:]) if is_id else getobj(slug=c)
        return self.category
    
    def get_url(self):
        if self.url is None:
            self.url = self.generate_url()
        return self.url

class CategoryView(BaseCategoryView):
    
    template_name = 'goods/categories.html'
    
    def generate_url(self):
        return '/categories/%s/' % self.get_category().as_url()
    
    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context.update({
            'category': self.get_category()
        })
        return context
    
class ProductView(TemplateResponseMixin, BaseDetailView):
    
    model = Product
    template_name = 'goods/product.html'
    
    def get_context_data(self, **kwargs):
        product = self.kwargs['pk']
        comments = list(Comment.get_tree().filter(
            product__id=product
        ))
        c = {
            'product': self.object,
            'comments': comments,
        }
        if self.request.user.is_authenticated():
            c['voted'] = [v.obj for v in Vote.objects.filter(
                obj__in=[cm.votingobject_ptr for cm in comments],
                owner=self.request.user.profile
            )]
        
        try:
            last = self.object.comment_set.get(
                owner=self.request.user,
                time__gt=datetime.datetime.now() - datetime.timedelta(seconds=3)
            )
            c['just_added'] = last
        except:
            pass
        return c

@unbanned_only
@login_required
class AddCommentView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('../')

    def post(self, request, product_id):
        text = request.POST.get('text')
        if text:
            answer_to = request.POST.get('answer_to')
            if answer_to:
                parent = Comment.objects.get(pk=answer_to)
                create_comment = parent.add_child
            else:
                create_comment = Comment.add_root
            create_comment(
                owner=self.request.user.profile,
                product_id=product_id,
                text=text,
                time=datetime.datetime.now(),
            )

        return HttpResponseRedirect('../')

class FullTreeView(TemplateView):
    template_name = 'goods/tree.html'

    def get_context_data(self, **kwargs):
        l = list(Category.objects.extra(
            select={'ord': 
                r"case inheritance when '' then ''"
                r" else inheritance || '.' end || id || '.'"
            },
            order_by=['ord',],
        ))
        objects = [{'category': i, 'nesting': range(0, i.depth())} for i in l]
        return {'objects': objects}

def vote(request, model, pk, mark, allow_self_vote=False, owner_field='owner'):
    c = model.objects.get(pk=pk)
    if not allow_self_vote and getattr(c, owner_field) == request.user.profile:
        return c, None
    return c, c.vote(request.user.profile, mark)

def try_ban(owner):
    new_comments = owner.comment_set.filter(
        time__gt=owner.unban_time
    ).only('votingobject_ptr')
    
    votes = Vote.objects.filter(obj__in=new_comments)
    avg = votes.aggregate(Avg('mark'))
    if avg.values()[0] < 0.3:
        owner.ban()
    return avg

@unbanned_only
@login_required
class CommentVoteView(View):
    http_method_names = ['post']

    def post(self, request, product_id, cid, mark):
        c, v = vote(request, Comment, cid, mark)
        try_ban(c.owner)
            

        return HttpResponseRedirect('../')