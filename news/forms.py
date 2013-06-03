from django.forms import ModelForm
from news.models import Entry

class PartialEntryForm(ModelForm):
    class Meta:
        model = Entry
        exclude = ('blog',)
