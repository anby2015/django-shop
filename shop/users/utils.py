import urlparse

from django.conf import settings

def get_prev_url(request):
    return request.META.get('HTTP_REFERER', '')

def get_redirect_url(request, redirect_field_name=settings.REDIRECT_FIELD_NAME):
    redir_to = request.REQUEST.get(redirect_field_name) or get_prev_url(request)
    
    # Security check -- don't allow redirection to a different host.
    netloc = urlparse.urlparse(redir_to)[1]
    if not redir_to or netloc and netloc != request.get_host():
        redir_to = settings.LOGIN_REDIRECT_URL
    return redir_to
