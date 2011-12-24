from django.db.models import Model, Avg, ForeignKey, IntegerField, ManyToManyField

from users.models import Profile

class VotingObject(Model):

	votes = ManyToManyField(Profile, through='Vote')

	def has_votes(self):
		return self.vote_set.exists()

	@property
	def highest_mark(self):
		raise NotImplementedError

	@property
	def lowest_mark(self):
		raise NotImplementedError
	
	@property
	def middle_mark(self):
		return (self.lowest_mark + self.highest_mark) / 2.0

	def is_shadowed(self):
		raise NotImplementedError
	
	def is_hidden(self):
		raise NotImplementedError

	def get_avg_mark(self):
		return self.vote_set.aggregate(Avg('mark')).values()[0]

	@property
	def mark(self):
		return self.get_avg_mark() if self.has_votes() else self.middle_mark

	def vote(self, user, mark):
		return self.vote_set.get_or_create(
			owner=user,
			defaults={'mark':mark}
		)


class Vote(Model):
	owner = ForeignKey(Profile)
	obj = ForeignKey(VotingObject)
	mark = IntegerField()