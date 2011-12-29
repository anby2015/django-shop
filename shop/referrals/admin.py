from django.contrib.admin import site
from referrals.models import Referrer
from treebeard.admin import TreeAdmin

site.register(Referrer, TreeAdmin)