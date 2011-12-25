"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from users.models import Profile
from goods.models import Comment
from goods.views import try_ban

def test_ban(comment=None):

	p = Profile.objects.get(username='forever_banned')
	c=comment or Comment.objects.filter(
		owner__user__username='forever_banned'
	).order_by('-time')[0]
	
	for i in range(0, 10):
		q, o_o = Profile.objects.get_or_create(username='qqq%d'%i)
		if i % 2 == 0:
			m = 1
		else: m = 0
		c.vote(q, m)

	for i in range(0, 10):
		d, o_o = Profile.objects.get_or_create(username='dis%d'%i)
		c.vote(d, 0)

	a = p.is_banned()
	# OUT: False
	b = try_ban(p)
	# OUT: {'mark__avg': 0.25}
	c = p.is_banned()
	# OUT: True
	return  a, b, c

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
