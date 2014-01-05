"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime

from django.test import TestCase
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from news.models import Entry
from django.utils.timezone import now as utcnow

def create_news(title, content, days):
    entry = Entry.objects.create(title=unicode(title),
                                 content=unicode(content),
                                 slug=slugify(title),
         created_at = utcnow() + datetime.timedelta(days=days))


class NewsIndexTests(TestCase):
    def test_index_view_with_no_news(self):
        """
        If no polls exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('news.views.index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No news.')
        self.assertQuerysetEqual(response.context['entry_list'], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be displayed on the index page.
        """
        create_news(title='Co dwa borsuki, to nie jeden', 
        content="and we'll create a factory method to create polls as well as a new test class:",
        days=-30)

        response = self.client.get(reverse('news.views.index'))
        self.assertQuerysetEqual(response.context['entry_list'], ['<Entry: Co dwa borsuki, to nie jeden>']
                )

