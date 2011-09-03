from django.forms import ModelForm, RegexField, EmailField
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from main.widgets import SelectDateWidget
from users.models import Profile

class AuthForm(AuthenticationForm):
    error_css_class = 'error'

class RegisterUserForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = ('username',)
    
    username = RegexField(label=_("Username"), max_length=30, regex=r'^[\w]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and _ only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and _ characters.")},
    )
    email = EmailField(label=_("Please, enter your e-mail for verification"), required=not settings.DEBUG)
    
    error_css_class = 'error'
    

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = (
            'first_name',
            'last_name',
            'birthday',
            'country',
            'city',
            'address',
        )
        widgets = {
            'birthday': SelectDateWidget(
                years=list(reversed(range(1905, 2006))),
                required=False,
                date_format='dmy',
                none_values={'d': 'Day:', 'm': 'Month:', 'y': 'Year:',}
            )
        }
