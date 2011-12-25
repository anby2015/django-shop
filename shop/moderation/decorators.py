from functools import wraps

from django.http import HttpResponseRedirect

from users.utils import get_prev_url

def unbanned_only(fun):
	@wraps(fun)
	def new_fun(request, *args, **kwargs):
		u = request.user
		if u.is_authenticated() and u.profile.is_banned():
			return HttpResponseRedirect(get_prev_url(request) or '../')
		return fun(request, *args, **kwargs)
	return new_fun