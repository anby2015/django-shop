from django.contrib.auth.forms import AuthenticationForm

def auth_form(request):
    def get_form():
        return AuthenticationForm()
    return {'auth_form': get_form}
