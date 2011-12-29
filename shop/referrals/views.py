from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from goods.models import Product
from users.models import Profile
from referrals.utils import is_person_referred_before, mark_user_referred

def ref_redirect(request, username, product_id):
	p = get_object_or_404(Product, pk=product_id)
	u = Profile.objects.filter(username=username)

	if u.exists() and request.user.is_anonymous():
		request.session['referrer'] = username

	return HttpResponseRedirect('/products/%s/' % str(product_id))
