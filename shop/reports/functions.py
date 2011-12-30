from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from cart.models import StorageItem

meta = {
	'Username':
		('storage__order__assignee__user', '"auth_user"."username"'),
	'Product':
		('product', '"goods_product"."name"'),
	'Country':
		('storage__order', '"cart_order"."country"'),
	'City':
		('storage__order', '"cart_order"."city"'),
	'Category':
		('product__category', '"goods_category"."name"'),
	'Year':
		('storage__order', 'strftime("%%%%y", "cart_order"."date")'),
	'Month':
		('storage__order', 'strftime("%%%%m", "cart_order"."date")'),
	'Day':
		('storage__order', 'strftime("%%%%y", "cart_order"."date")'),
}

class NotEnoughArguments(Exception): pass

def get_report_matrix_query(*args):
	if len(args) != 2:
		raise NotEnoughArguments()
	x= (meta[i] for i in args)
	rels, fields = zip(*tuple(x))
	params = ('param1', 'param2',)
	q = StorageItem.objects.all().select_related('product', *rels).extra(
		select=dict(zip(params, fields), **{
			'report_sum': 'SUM("goods_product"."cost"*count)',
		}),
		order_by=list(params),
	)
	s, o = tuple(str(q.query).split('ORDER BY'))
	query = s + ' GROUP BY ' + ', '.join(params) + ' ORDER BY ' + o

	return StorageItem.objects.raw(query)

def get_report_matrix(param1, param2, query=None, fill_empty=True):
	q = query or get_report_matrix_query(param1, param2)
	m = {}
	l1, l2 = set(), set()
	for i in q:
		m.setdefault(i.param1, {})
		m[i.param1][i.param2] = i.report_sum
		l1.add(i.param1)
		l2.add(i.param2)

	if fill_empty:
		for k, v in m.iteritems():
			for j in l2:
				v.setdefault(j, 0.0)
	return m, l1, l2

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