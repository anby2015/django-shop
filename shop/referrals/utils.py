def is_person_referred_before(request):
	'''
	This should check if some person already
	participated in referral system.
	Here ve can try to avoid possible hacks
	with spamming of hotlinking and fake registration.
	Or just faithfully check some simple stuff=)
	'''
	return \
		request.user.is_authenticated() or \
		'referrer' in request.session

def mark_user_referred(request, username):
	'''
	Marks the person if he was referred by
	the user.
	This also can write some request data
	to help in preventing of referral hacks.
	'''
	request.session['referrer'] = username