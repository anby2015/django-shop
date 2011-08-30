from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout as auth_logout, REDIRECT_FIELD_NAME as AUTH_REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.conf import settings
from django.views.decorators.http import require_POST

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

class LoginView(FormView):
    """
    A bit generic class-based login view
    appears as rework of django.contirb.auth.views.login
    """
    
    form_class = AuthenticationForm
    redirect_field_name = settings.REDIRECT_FIELD_NAME
    template_name = 'users/login.html'

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs) 

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

@require_POST
@login_required
def logout(request):
    auth_logout(request.user)
    return HttpResponseRedirect(get_redirect_url(request))

