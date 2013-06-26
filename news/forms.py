from django.forms import ModelForm
from news.models import Entry, CustomPage

class PartialEntryForm(ModelForm):
    class Meta:
        model = Entry
        exclude = ('blog',)

class PartialCustomPageForm(ModelForm):
    class Meta:
        model = CustomPage
        exclude = ('blog',)
