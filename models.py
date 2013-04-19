from django.db import models
from django.core.urlresolvers import reverse

from django.utils.timezone import now as utcnow
now = utcnow() # replacing - date.now() causes problems with auto_now_add

# TODO: set Site for 'View on site'

class PublicEntryManager(models.Manager):
    def get_query_set(self):
        return super(PublicEntryManager, self).get_query_set().filter(created_at__lt=utcnow())

class Entry(models.Model):
    created_at = models.DateTimeField(default=now, editable=False)
    title      = models.CharField(max_length = 50)
    content    = models.TextField()
    slug       = models.SlugField(unique=True) # unique_for_date is buggy
    objects    = models.Manager() # default manager
    public     = PublicEntryManager() # without entries from future
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        y = str(self.created_at.year)
        m = str(self.created_at.month).rjust(2, '0')
        d = str(self.created_at.day).rjust(2, '0')
        sl = self.slug
        return reverse('news.views.detail', kwargs={'year': y, 'month': m, 'day': d, 'slug': sl})
    def prev_entry(self):
        try:
            result = Entry.public.filter(created_at__lt=self.created_at)[0]
        except IndexError:
            result = None
        return result
    def next_entry(self):
        try:
            result = Entry.public.filter(created_at__gt=self.created_at).reverse()[0]
        except IndexError:
            result = None
        return result
    class Meta:
        ordering = ['-created_at']

class EntryComment(models.Model):
    entry = models.ForeignKey(Entry)
    created_at = models.DateTimeField(default=now, editable=False)
    content = models.TextField()
    signature = models.CharField(max_length = 20)
