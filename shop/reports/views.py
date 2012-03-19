from datetime import datetime
from collections import OrderedDict

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.generic.base import View, TemplateResponseMixin, TemplateView
from django.utils import simplejson as json
from django.core.paginator import Paginator, EmptyPage

from goods.views import PAGINATE_BY
from reports.functions import get_report_matrix, meta, generate_pdf, filters, f_list, display
from reports.models import Filter

def get_matrix_from_request(request, where=None):
		get = request.REQUEST.get
		params = get('param1'), get('param2')
		e = True#get('show_empty', False)
		try:
			if where is None:
				where = request.user.profile.filter.data
		except:
			where = None
		finally:
			m = get_report_matrix(*params, fill_empty=e, wherein=where) \
				if params[0] and params[1] else None
			return m, params

class ReportView(TemplateView):
	template_name = 'reports/index.html'
	def get_context_data(self, **kwargs):
		m, params = get_matrix_from_request(self.request)
		_d = json.dumps if not self.request.is_ajax() else lambda v: v
		ctx = {}
		if m:
			m, l1, l2 = m
			
			t = []
			for i in l2:
				l = []
				for j in l1:
					l += [m[j][i]]
				t += [l]

			ctx = {
				'map': _d(t),
				'paramsy': _d(list(l2)),
				'paramsx': _d(list(l1)),
			}

			if not self.request.is_ajax():
				ctx.update({
					'matrix': m,
					'param1': params[0],
					'param2': params[1],
					'filters': _d(f_list),
				})
		if not self.request.is_ajax():
			ctx['fields'] = meta
		return ctx

	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			js = self.get_context_data()
			return HttpResponse(json.dumps(js))
		else:
			return super(ReportView, self).get(request, *args, **kwargs)


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


class FilterView(View):
	def get(self, request, *args, **kwargs):
		get = request.REQUEST.get
		f = get('f')
		page_index = get('page')

		if f not in meta:
			raise Http404

		p = Paginator(filters[f](), PAGINATE_BY)
		try:
			page = p.page(int(page_index) + 1)
		except TypeError:
			page = p.page(1)
		except EmptyPage:
			raise Http404
		data = request.user.profile.filter.data.get(f, {})
		saved = data.get('list', '')
		ctx = {
			'list': list(page.object_list),
			'page_count': p.num_pages,
			'saved': [{
				'id': i,
				'name': display(i, f)
			} for i in saved],
			'exclude': data.get('exclude', 1)
		}
		return HttpResponse(json.dumps(ctx))

	def post(self, request, *args, **kwargs):
		r = request.POST
		if r.get('save') is not None:
			o, created = Filter.objects.get_or_create(user=request.user.profile)
			d = {} if created else o.data
			for f in f_list:
				fld = 'filter_' + f
				
				if fld not in r:
					continue
				d[f] = {
					'exclude': int(bool(r.get('exclude_' + f))),
					'list': r.getlist(fld),
				}
			o.data = d
			o.save()
		return HttpResponse('')



