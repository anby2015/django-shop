from django.db import models
from django.db.models import IntegerField, DateField, CharField, TextField, OneToOneField
from django.contrib.auth.models import User

from users.fields import CountryField

GENDER_CHOICES = (
    (0, 'Not sure'),
    (1, 'Male'),
    (2, 'Female'),
)

EMPTY = {'null': True, 'blank': True}

class Profile(User):
    # p.user is much trettier then p.user_ptr
    user = OneToOneField(User, parent_link=True)
    
    gender = IntegerField(choices=GENDER_CHOICES, default=0, **EMPTY)
    birthday = DateField(**EMPTY)
    country = CountryField(**EMPTY)
    city = CharField(max_length=200, **EMPTY)
    adress = TextField(**EMPTY)
