from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import FormView, BaseCreateView, BaseUpdateView
from django.contrib.auth import login, logout, authenticate, REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.conf import settings
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render

from main.class_decorators import login_required, csrf_protect, never_cache, unauthorized_only
from users.forms import AuthForm, RegisterUserForm, ProfileForm
from users.models import Profile
from users.utils import get_prev_url, get_redirect_url

require_GET_POST = require_http_methods(['GET', 'POST'])

if not hasattr(settings, 'REDIRECT_FIELD_NAME'):
    setattr(settings, 'REDIRECT_FIELD_NAME', REDIRECT_FIELD_NAME)

class AuthMixin(object):
    
    redirect_field_name = settings.REDIRECT_FIELD_NAME
    
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
    

@csrf_protect
@never_cache
@unauthorized_only
class Login(AuthMixin, FormView):
    """
    A bit generic class-based login view
    appears as rework of django.contirb.auth.views.login
    customized for own needs
    """
    
    form_class = AuthForm
    template_name = 'users/login.html'
    
    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(Login, self).form_valid(form)
    

@login_required
class Logout(View):
    
    def get(self, request):
        # user typed '/logout/' into browser address bar
        # we want to know, if he is sure he wants to logout to prevent csrf
        return render(request, 'users/logout.html', {})
    
    def post(self, request):
        logout(request)
        return HttpResponseRedirect(get_redirect_url(request))
    

@csrf_protect
@never_cache
@unauthorized_only
class Register(AuthMixin, TemplateResponseMixin, BaseCreateView):
    
    form_class = RegisterUserForm
    template_name = 'users/create.html'
    success_url = '/thanks/'
    
    def get_success_url(self):
        return '%s?%s=%s' % (
            self.success_url,
            self.redirect_field_name,
            self.get_redirect_url(),
        )

    def form_valid(self, form):
        res = super(Register, self).form_valid(form)
        self.object.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, self.object)
        return res
    
    
class ProfileMixin(object):

    def get_object(self):
        return self.request.user.profile
    

class BaseProfileUpdateView(TemplateResponseMixin, ProfileMixin, BaseUpdateView):
    
    form_class = ProfileForm
    

@login_required
class CompleteRegistration(AuthMixin, BaseProfileUpdateView):
    
    template_name = 'users/complete_registration.html'
