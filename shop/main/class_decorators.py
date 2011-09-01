import new
from functools import wraps, partial

from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormMixin

# start patching decorators import
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
# end patching decorators import

def patches(method_name, deco=None):
    '''
    decorator factory that pathches function decorator to decorate class,
    actually decorating the specified class method
    
    usage:
    class A:
        def f(*args, **kwargs):
            ...
    class_f_deco = patches('f', deco)
    @class_f_deco
    class B(A):
        ...
    
    actually it is replacement for
    class B(A):
        @method_decorator(deco)
        def f(*args, **kwargs):
            return super(B, self).f(*args, **kwargs)
    '''
    def deco_deco(deco):
        @wraps(deco) # never mind, just let it be
        def cls_deco(cls):
            old_func = getattr(cls, method_name)
            new_func = method_decorator(deco)(old_func)
            setattr(cls, method_name, wraps(old_func)(new_func))
            return cls
        return cls_deco
        
    return deco_deco(deco) if deco else deco_deco

patches_view = patches('dispatch')
# do not use `patches_view` for patching `require_http_methods`!
# use `View.http_method_names` instead!

login_required = patches_view(login_required)
csrf_protect = patches_view(csrf_protect)
never_cache = patches_view(never_cache)

def patch_method(default=None):
    'class decorator factory. decorates method with specified name'
    decorator_passed = callable(default)
    def real_factory(deco):
        def _new_deco(method):
            def actual_decorator(cls):
                setattr(cls, method, deco(getattr(cls, method)))
                return cls
            return actual_decorator
        
        if default or not decorator_passed:
            def new_deco(method=default):
                if isinstance(method, basestring):
                    return lambda cls: _new_deco(method)(cls)
                return _new_deco(default)(method)
        else:
            new_deco = _new_deco
        return wraps(deco)(new_deco)
    
    return real_factory(default) if decorator_passed else real_factory

@patch_method('dispatch')
def unauthorized_only(method):
    '''
    used for Login and Register views.
    do not leave authorised users a chance to register or login again
    class instance needs `get_redirect_url` method
    '''
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            self.request = request
            response = HttpResponseRedirect(self.get_redirect_url())
        else:
            response = method(self, request, *args, **kwargs)
        return response
    return dispatch
