from django.db.models import Model, OneToOneField, TextField

from users.models import Profile
from reports.jsonfield import JSONField

class Filter(Model):
	user = OneToOneField(Profile)
	data = JSONField(blank=True)