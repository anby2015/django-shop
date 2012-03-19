from django.conf.urls.defaults import patterns, url

from reports.views import ReportView, GenPdfView, FilterView

urlpatterns = patterns('reports.views',
	(r'^$', ReportView.as_view(),),
	(r'^gen_pdf/$', GenPdfView.as_view(),),
	(r'^load_filter/$', FilterView.as_view(),),
)