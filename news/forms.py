from django.forms import ModelForm
from news.models import Entry, Comment

class EntryForm(ModelForm):
    class Meta:
        model = Entry

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('entry')
