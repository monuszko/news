from django.forms import ModelForm
from news.models import Entry, Comment

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('entry')
