from django.contrib import admin

from users.models import Profile
from users.forms import ProfileForm

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    form = ProfileForm
    

admin.site.register(Profile, ProfileAdmin)
