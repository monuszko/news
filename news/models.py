from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now # date.now() malfunctions with auto_now_add
from django.core.exceptions import ValidationError
import django.core.validators as vali

# TODO: set Site for 'View on site'

class PublicEntryManager(models.Manager):
    def get_query_set(self):
        return super(PublicEntryManager, self).get_query_set().filter(created_at__lt=now())

# TODO: implement pub_date separate from created_at


class Blog(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.TextField()
    author  = models.OneToOneField(User)

    def __unicode__(self):
        return self.name

# Flatpages are problematic in multi-user environment
class CustomPage(models.Model):
    url = models.CharField(max_length=100, db_index=True, validators=[vali.validate_slug], 
            error_messages={'invalid': 'Allowed characters: a-z0-9_' }) # admin - podpowiedz
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    blog = models.ForeignKey(Blog)

    class Meta:
        ordering = ('url',)
        unique_together = ('blog', 'url') #TODO: Doesn't prevent adding via view!

    def __unicode__(self):
        return u"{0} -- {1}".format(self.url, self.title)

    def get_absolute_url(self):
        return reverse('news:custom_page', kwargs={'blogname': self.blog.author.username, 'page': self.url.strip('/')})

class Entry(models.Model):
    blog       = models.ForeignKey(Blog)
    created_at = models.DateTimeField(default=now, editable=False)
    title      = models.CharField(max_length = 50)
    content    = models.TextField()
    slug       = models.SlugField() # unique_for_date is buggy
    objects    = models.Manager() # default manager
    class Meta:
        unique_together = ('blog', 'slug')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        y = str(self.created_at.year)
        m = str(self.created_at.month).rjust(2, '0')
        d = str(self.created_at.day).rjust(2, '0')
        sl = self.slug
        return reverse('news:detail', kwargs={'blogname': self.blog.author.username, 'year': y, 'month': m, 'day': d, 'slug': sl})

    def prev_entry(self):
        try:
            result = Entry.objects.filter(blog=self.blog,
                                         created_at__lt=self.created_at)[0]
        except IndexError:
            result = None
        return result

    def next_entry(self):
        try:
            result = Entry.objects.filter(blog=self.blog,
                                   created_at__gt=self.created_at).reverse()[0]
        except IndexError:
            result = None
        return result

    class Meta:
        ordering = ['-created_at']
