import re
from collections import OrderedDict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from cart.models import StorageItem
from users.fields import COUNTRIES

meta = {
	'Username':
		('storage__order__assignee__user', '"auth_user"."username"'),
	'User\'s first name':
		('storage__order__assignee__user', '"auth_user"."first_name"'),
	'Product':
		('product', '"goods_product"."name"'),
	'Country':
		('storage__order', '"cart_order"."country"'),
	'City':
		('storage__order', '"cart_order"."city"'),
	'Category':
		('product__category', '"goods_category"."name"'),
	'Year':
		('storage__order', 'strftime("%%%%Y", "cart_order"."date")'),
	'Month':
		('storage__order', 'strftime("%%%%m", "cart_order"."date")'),
	'Day':
		('storage__order', 'strftime("%%%%d", "cart_order"."date")'),
}

filter_meta = {
	'Username':
		'username',
	'User\'s first name':
		'first_name',
	'Product':
		'name',
	'Country':
		'country',
	'City':
		'city',
	'Category':
		'name',
	'Year':
		'year',
	'Month':
		'month',
	'Day':
		'day',
}

isiterable = lambda o: getattr(o, '__iter__', False)

class NotEnoughArguments(Exception): pass

def get_report_matrix_query(*args, **extra):
	if len(args) != 2:
		raise NotEnoughArguments()
	x = (meta[i] for i in args)
	rels, fields = zip(*tuple(x))
	params = ('param1', 'param2',)
	
	select = dict(zip(params, fields))
	if extra.get('aggregate'):
		select['report_sum'] = \
			'SUM("goods_product"."cost"*"cart_storageitem"."count")'

	filter_dict, exclude_dict = {}, {}
	for k, v in extra.get('wherein', {}).iteritems():
		w = exclude_dict if v.get('exclude', 1) else filter_dict
		l = ['"%s"' % i for i in v['list']]
		key = '%s__%s__in' % (meta[k][0], filter_meta[k])
		w[key] = l

	order = extra.get('order', True)
	order_by = list(params) if order and isinstance(order, bool) else []
	if isinstance(order, str):
		order = (order,)

	q = StorageItem.objects.all().\
		select_related('product', 'storage__order', *rels).\
		filter(**filter_dict).exclude(**exclude_dict).\
		extra(
			select=select,
			order_by=order_by,
			where=['"cart_order"."storage_ptr_id" IS NOT NULL']
		)

	if isiterable(order):
		q = q.order_by(tuple(order))

	distinct = extra.get('distinct', False)
	if distinct is not False:
		distinct = tuple(distinct) if isiterable(distinct) else (distinct,)
		q = q.distinct(*distinct)

	l = str(q.query).split('ORDER BY')
	s, o = 'ORDER BY'.join(l[:-1]), l[-1]
	
	query = (s or o) + ' GROUP BY ' + ', '.join(params)
	if len(l) > 1:
		query += ' ORDER BY ' + o

	sub = r'\s*(SELECT (.* AS "report_sum",)?.* AS "param2", .* AS "param1").* FROM' #first 3 fields
	repl = r'\1, "cart_storageitem"."id" FROM '
	#substitution doesnt work anymore :-(
	#query = re.subn(sub, repl, query, flags=re.M and re.S)[0]
	

	return StorageItem.objects.raw(query)

display_dict = {
	'Country': dict(COUNTRIES),
}

def display(fld, param):
	return display_dict.get(param, {}).get(fld, fld)

def get_report_matrix(param1, param2,
		query=None, fill_empty=True, wherein=None):
	
	q = query or \
		get_report_matrix_query(param1, param2, aggregate=True, wherein=wherein)
	m = OrderedDict()
	l1, l2 = set(), set()
	for i in q:
		p1, p2 = display(i.param1, param1), display(i.param2, param2)
		m.setdefault(p1, {})
		m[p1][p2] = i.report_sum
		l1.add(p1)
		l2.add(p2)
	if fill_empty:
		for k, v in m.iteritems():
			for j in l2:
				v.setdefault(j, 0.0)
	return m, sorted(l1), sorted(l2)

def generate_pdf(filename, table, fill_empty=True):
	doc = SimpleDocTemplate(filename, pagesize=letter)
	elements = []
	t = Table(table)
	elements = [t]
	t.setStyle(TableStyle([
		('ALIGN',(1,1),(-1,-1), 'RIGHT'),
		('TEXTCOLOR',(0,1),(0,-1),colors.red),
		('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
		('TEXTCOLOR',(1,0),(-1,0),colors.red),
		('BOX', (0,0), (0,-1), 2.0, colors.black),
		('BOX', (0,0), (-1,0), 2.0, colors.black),
		('BOX', (1,1), (-1,-1), 0.25, colors.black),
	]))
	doc.build([t])

def _report_matrix_lambda_factory(f, **kws):
	return lambda: [{
		'id': i.param1,
		'name': display(i.param1, f),
	} for i in get_report_matrix_query(f, f, distinct=True, **kws)]

f_list = ['User\'s first name', 'Country', 'City', 'Category', 'Year']
filters = {
	f: _report_matrix_lambda_factory(f) for f in f_list
}
f_list += ['Day', 'Month']
f_list.insert(-1, 'Product')
filters.update({
	'Day': lambda: range(1, 32),
	'Month': lambda: range(1, 13),
	'Product': _report_matrix_lambda_factory('Product', order=False)
})
