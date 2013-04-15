from django.conf.urls import patterns, url

urlpatterns = patterns('news.views',
        url(r'^$', 'index'),
        url(r'^form/$', 'form'),
        url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', 'detail'),
        url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'day_archive'),
        url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'month_archive'),
        url(r'^(?P<year>\d{4})/$', 'year_archive'),
        )


# 2004/12/15/Joel-is-a-slug
