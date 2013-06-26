from django.conf.urls import patterns, include, url
from news import views

urlpatterns = patterns('',
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/$', views.index, name='index'),
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/post/$', views.post, name='post'),
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', views.detail, name='detail'),
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/edit/$', views.edit_entry, name='edit_entry'),
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.day_archive, name='day_archive'),
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/(?P<year>\d{4})/(?P<month>\d{2})/$', views.month_archive, name='month_archive'),
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/(?P<year>\d{4})/$', views.year_archive, name='year_archive'),
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/create/$', views.create, name='create'),
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/pages/(?P<page>[a-zA-Z0-9_-]+)/edit/$', views.edit_page, name='edit_page'),
        url(r'^(?P<blogname>[a-zA-Z0-9]+)/pages/(?P<page>[a-zA-Z0-9_-]+)/$', views.custom_page, name='custom_page'),
        )
