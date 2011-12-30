from django.conf.urls.defaults import patterns, url

from reports.views import ReportView, GenPdfView

urlpatterns = patterns('',
	(r'^$', ReportView.as_view(),),
	(r'^gen_pdf/$', GenPdfView.as_view(),),
)