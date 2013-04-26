from django.conf.urls import patterns, url
from news import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', views.detail, name='detail'),
        url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.day_archive, name='day_archive'),
        url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', views.month_archive, name='month_archive'),
        url(r'^(?P<year>\d{4})/$', views.year_archive, name='year_archive'),
        )

