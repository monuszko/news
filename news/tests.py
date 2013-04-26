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

def create_entry(title, content, days):
    entry = Entry.objects.create(title=unicode(title),
                                 content=unicode(content),
                                 slug=slugify(title),
         created_at = utcnow() + datetime.timedelta(days=days))
    return entry


class NewsIndexTests(TestCase):
    def test_index_view_with_no_entries(self):
        """
        If no entries exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('news:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No news.')
        self.assertQuerysetEqual(response.context['entry_list'], [])

    def test_index_view_with_a_past_entry(self):
        """
        Polls with a pub_date in the past should be displayed on the index page.
        """
        create_entry(title='A past entry', 
        content="and we'll create a factory method to create polls as well as a new test class:",
        days=-30)

        response = self.client.get(reverse('news:index'))
        self.assertQuerysetEqual(response.context['entry_list'], ['<Entry: A past entry>'])

    def test_index_view_with_a_future_entry(self):
        """
        Entries with a created_at date in the future should not be displayed on the index page.
        """
        create_entry(title='Lepszy wrobel w garsci, niz skrzypek na dachu', 
                    days=30,
                    content="""Keeping URIs so that they will still be around in 2, 20 or 200
                            or even 2000 years is clearly not as simple as it sounds. However, all
                            over the Web, webmasters are making decisions which will make it really
                            difficult for themselves in the future. Often, this is because they are
                            using tools whose task is seen as to present the best site in the
                            moment, and no one has evaluated what will happen to the links when
                            things change. The message here is, however, that many, many things can
                            change and your URIs can and should stay the same. They only can if you
                            think about how you design them.""")
        response = self.client.get(reverse('news:index'))
        self.assertContains(response, "No news.", status_code=200)
        self.assertQuerysetEqual(response.context['entry_list'], []
        )

    def test_index_view_with_a_future_entry_and_past_entry(self):
        """"
        Even if both past and future entries exist, only past entries should be displayed.
        """
        create_entry(title='A past entry',
        content="and we'll create a factory method to create polls as well as a new test class:",
        days=-30)
        create_entry(title='A future entry',
        content="_.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-.",
        days=30)
        response = self.client.get(reverse('news:index'))
        self.assertQuerysetEqual(
                response.context['entry_list'], ['<Entry: A past entry>']
        )

    def test_index_view_with_two_past_entries(self):
        create_entry(title='Past entry 1', content="Borsuk", days=-30)
        create_entry(title='Past entry 2', content="Pies", days=-5)
        response = self.client.get(reverse('news:index'))
        self.assertQuerysetEqual(response.context['entry_list'],
                ['<Entry: Past entry 2>', '<Entry: Past entry 1>']
        )


class NewsDetailTests(TestCase):
    def test_detail_view_with_a_future_entry(self):
        """
        The detail view of an entry with a created_at date
        in the future should return a 404 not found.
        """
        future_entry = create_entry(title='Future Entry', content='Abc',
                days=6)
        response = self.client.get(future_entry.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_entry(self):
        """
        The detail view of an entry with a created_at date in the past should
        display the entry's title.
        """
        past_entry = create_entry(title='Past Entry', content='Def',
                days=-6)
        response = self.client.get(past_entry.get_absolute_url())
        self.assertContains(response, past_entry.title, status_code=200)

