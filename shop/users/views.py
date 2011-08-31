from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import FormView, BaseCreateView
from django.contrib.auth import login, logout as auth_logout, REDIRECT_FIELD_NAME as AUTH_REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.conf import settings
from django.views.decorators.http import require_POST, require_http_methods

from main.class_decorators import login_required, csrf_protect, never_cache, unauthorized_only
from users.forms import RegisterUserForm

require_GET_POST = require_http_methods(['GET', 'POST'])

if not hasattr(settings, 'REDIRECT_FIELD_NAME'):
    setattr(settings, 'REDIRECT_FIELD_NAME', AUTH_REDIRECT_FIELD_NAME)

def get_prev_url(request):
    return request.META.get('HTTP_REFERRER', '')

def get_redirect_url(request, redirect_field_name=settings.REDIRECT_FIELD_NAME):
    redir_to = request.REQUEST.get(redirect_field_name) or get_prev_url(request)

    # Security check -- don't allow redirection to a different host.
    netloc = urlparse.urlparse(redirect_to)[1]
    if not redir_to or netloc and netloc != request.get_host():
        redir_to = settings.LOGIN_REDIRECT_URL
    return redir_to

@csrf_protect
@never_cache
@unauthorized_only
class LoginView(FormView):
    """
    A bit generic class-based login view
    appears as rework of django.contirb.auth.views.login
    customized for own needs
    """

    form_class = AuthenticationForm
    redirect_field_name = settings.REDIRECT_FIELD_NAME
    template_name = 'users/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView

    def get_redirect_url(self):
        return get_redirect_url(self.request, self.redirect_field_name)

    def get_success_url(self):
        return self.success_url or self.get_redirect_url()
    
    def get_context_data(self, **kwargs):
        data = {
            'redirect_field_name': self.redirect_field_name,
            'redirect_url': self.get_redirect_url(),
        }
        data.update(kwargs)
        return data

@login_required
class Logout(View):
    def post(request):
        auth_logout(request.user)
        return HttpResponseRedirect(get_redirect_url(request))

@csrf_protect
@never_cache
@unauthorized_only
class Register(TemplateResponseMixin, BaseCreateView):

    form_class = RegisterUserForm
    redirect_field_name = settings.REDIRECT_FIELD_NAME
    template_name = 'users/create.html'

    get_context_data = LoginView.get_context_data
