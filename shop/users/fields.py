from django.db import models

from users.countries import COUNTRIES

#adapted from http://www.djangosnippets.org/snippets/494/
#and http://djangosnippets.org/snippets/1281/
#using UN country and 3 char code list
#from http://unstats.un.org/unsd/methods/m49/m49alpha.htm


class CountryField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 3)
        kwargs.setdefault('choices', COUNTRIES)

        super(CountryField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"
