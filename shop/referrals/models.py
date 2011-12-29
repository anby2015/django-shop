from django.db.models import OneToOneField
from treebeard.mp_tree import MP_Node

from users.models import Profile

class Referrer(MP_Node):
	profile = OneToOneField(Profile, null=True)
	
	def __unicode__(self):
		return '%s (%.3f)' % (self.profile.username, self.profile.fee,)