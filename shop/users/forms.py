from django.forms import ModelForm, RegexField
from django.conf.settings import DEBUG
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from users.models import Profile

class RegisterUserForm(UserCreationForm):
	username = RegexField(label=_("Username"), max_length=30, regex=r'^[\w]+$',
		help_text = _("Required. 30 characters or fewer. Letters, digits and _ only."),
		error_messages = {'invalid': _("This value may contain only letters, numbers and _ characters.")},
	)
	email = EmailField(label=_("Please, enter your e-mail for verification"), required=not DEBUG)
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
        )
