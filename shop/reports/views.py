from datetime import datetime
from collections import OrderedDict

from django.http import HttpResponseRedirect
from django.views.generic.base import View, TemplateResponseMixin, TemplateView
from django.utils import simplejson as json

from reports.functions import get_report_matrix, meta, generate_pdf

def get_matrix_from_request(request):
		get = request.REQUEST.get
		params = get('param1'), get('param2')
		e = True#get('show_empty', False)
		m = get_report_matrix(*params, fill_empty=e) if params[0] and params[1] else None
		return m, params

class ReportView(TemplateView):
	template_name = 'reports/index.html'
	def get_context_data(self, **kwargs):
		ctx = {
			'fields': meta,
		}
		m, params = get_matrix_from_request(self.request)
		_d = json.dumps
		if m:
			m, l1, l2 = m
			
			t = []
			for i in l2:
				l = []
				for j in l1:
					l += [m[j][i]]
				t += [l]

			ctx.update({
				'matrix': m,
				'param1': params[0],
				'param2': params[1],
				'map': _d(t),
				'paramsy': _d(list(l2)),
				'paramsx': _d(list(l1)),
			})
		return ctx

class GenPdfView(View):
	def post(self, request, *args, **kwargs):
		d = 'static/pdf/%s' % request.user.username
		from os import system
		system('mkdir -p ' + d)
		path = '%s/%s.pdf' % (d, str(datetime.now()))
		m, params = get_matrix_from_request(request)
		if m:
			m, l1, l2 = m
			t = [['%.2f' % i for i in v.values()] for k, v in m.iteritems()]
			for l, h in zip(t, l1):
				l.insert(0, h)
			t = [['%s/%s' % params] + m.values()[0].keys()] + t
			generate_pdf(path, t)
		return HttpResponseRedirect('/' + path)