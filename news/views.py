from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from news.forms import EntryForm
from news.models import Entry

def index(request):
    entry_list = Entry.objects.all()
    return render_to_response('news/index.html', {'entry_list': entry_list})


def form(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/news')
    else:
        form = EntryForm()

    return render_to_response('news/form.html', {'form': form},
                                      context_instance=RequestContext(request))
