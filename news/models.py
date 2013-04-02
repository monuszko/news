from django.db import models

class Entry(models.Model):
    created_at = models.DateTimeField(auto_now_add = True)
    title      = models.CharField(max_length = 200)
    content    = models.TextField()
    def __unicode__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']

