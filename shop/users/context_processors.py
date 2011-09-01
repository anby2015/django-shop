from django.contrib.auth.forms import AuthenticationForm

def auth_form(requet):
    def get_form():
        return AuthenticationForm()
    return {'auth_form': get_form}
