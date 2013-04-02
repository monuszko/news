from django.forms import ModelForm
from news.models import Entry

class EntryForm(ModelForm):
    class Meta:
        model = Entry
