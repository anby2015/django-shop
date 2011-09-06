import sys

from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms.fields import BooleanField
from django.forms.models import ModelForm
from django.utils.translation import ugettext, ugettext_lazy as _

auth_admin_loaded = 'django.contrib.auth.admin' in sys.modules
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from main.widgets import SelectDateWidget
from users.models import Profile
from users.forms import ProfileForm
    
MODERATOR_PERMISSIONS = [
    'users.change_profile',
    'users.delete_profile',
    'users.add_profile'
]

is_moderator_field = lambda: BooleanField(
    required=False,
    label='Moderator',
    help_text='Designates whether the user can operate with profiles.',
)

def save_profile(p, is_moderator):
    if is_moderator:
        p.is_staff = True
        for perm in MODERATOR_PERMISSIONS:
            p.user_permissions.add(perm)

class AdmiProfileFormMixin(object):
    def save_profile(self, caller_class, commit):
        p = super(caller_class, self).save(commit=False)
        save_profile(p, self.cleaned_data['is_moderator'])
        if commit:
            p.save()
        return p

class AdminProfileChangeForm(AdmiProfileFormMixin, UserChangeForm):    
    class Meta(UserChangeForm.Meta):
        model = Profile
        
    is_moderator = is_moderator_field()
    
    def save(self, commit=True):
        return self.save_profile(AdminProfileChangeForm, commit)
    

class AdminProfileCreateForm(AdmiProfileFormMixin, UserCreationForm):
    class Meta:
        model = Profile
        
    is_moderator = is_moderator_field()
    
    def save(self, commit=True):
        return self.save_profile(AdminProfileCreateForm, commit)
        
class ProfileAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name')
    form = AdminProfileChangeForm
    add_form = AdminProfileCreateForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (('first_name', 'last_name'), 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_moderator')}),
        (_('Profile Information'), {'fields': ('gender', 'birthday', 'country', 'city', 'address',)}),
    )
    add_fieldsets = ( # duplicate, didn't change yet
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
    )
    

admin.site.register(Profile, ProfileAdmin)

# as we are importing auth.admin, sites suited there are registering, too
# we don't want this
if not auth_admin_loaded:
    admin.site.unregister((User, Group,))
