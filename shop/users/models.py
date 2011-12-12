from django.conf import settings
from django.db import models
from django.db.models import IntegerField, DateField, CharField, TextField, OneToOneField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from users.fields import CountryField

GENDER_CHOICES = (
    (0, 'Not sure'),
    (1, 'Male'),
    (2, 'Female'),
)

EMPTY = {'null': True, 'blank': True}

class Profile(User):
    # p.user is much prettier then p.user_ptr
    user = OneToOneField(User, parent_link=True)
    
    gender = IntegerField(choices=GENDER_CHOICES, default=0, **EMPTY)
    birthday = DateField(**EMPTY)
    country = CountryField(**EMPTY)
    city = CharField(max_length=200, **EMPTY)
    address = TextField(**EMPTY)

    def get_full_address(self):
        return '%s, %s, %s' % (self.address, self.city, self.country,)
    

@receiver(pre_save, sender=Profile)
def pre_save_profile(sender, instance, *args, **kwargs):
    instance.is_staff = instance.username in settings.MAIN_ADMINS
    instance.is_superuser = instance.is_staff
