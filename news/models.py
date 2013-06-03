from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now # date.now() malfunctions with auto_now_add

# TODO: set Site for 'View on site'

def validate_alnum(value):
    if not value.isalnum():
        raise ValidationError(u'Blog name is not alphanumeric')

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


class Entry(models.Model):
    blog       = models.ForeignKey(Blog)
    created_at = models.DateTimeField(default=now, editable=False)
    title      = models.CharField(max_length = 50)
    content    = models.TextField()
    slug       = models.SlugField() # unique_for_date is buggy
    objects    = models.Manager() # default manager
    public     = PublicEntryManager() # without entries from future
    class Meta:
        unique_together = ('slug', 'blog')

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
            result = Entry.public.filter(blog=self.blog,
                                         created_at__lt=self.created_at)[0]
        except IndexError:
            result = None
        return result
    def next_entry(self):
        try:
            result = Entry.public.filter(blog=self.blog,
                                   created_at__gt=self.created_at).reverse()[0]
        except IndexError:
            result = None
        return result
    class Meta:
        ordering = ['-created_at']
