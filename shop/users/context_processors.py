from django.contrib.auth.forms import AuthenticationForm

def auth_form(request):
    def get_form():
        return AuthenticationForm()
    return {'auth_form': get_form}

def users_ip(request):
	return request.META['REMOTE_ADDR']