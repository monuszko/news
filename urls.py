from django.conf.urls import patterns, url

urlpatterns = patterns('news.views',
        url(r'^$', 'index'),
        url(r'^form/$', 'form'),
        )

