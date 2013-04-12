from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from news.forms import EntryForm
from news.models import Entry
from django.utils.timezone import utc
import datetime

def index(request):
    entry_list = Entry.objects.all()
    return render_to_response('news/index.html', {'entry_list': entry_list})


# TODO: 404 ?

def detail(request, year, month, day, slug):
    e = Entry.objects.get(slug=slug)
    prev_entry = e.prev_entry()
    next_entry = e.next_entry()
    return render_to_response('news/detail.html', {'entry': e, 'prev_entry': prev_entry, 'next_entry': next_entry})


def day_archive(request, year, month, day):
    cd = datetime.datetime(int(year), int(month), int(day)).replace(tzinfo=utc)
    one_day = datetime.timedelta(days=1)
    # TODO: Test against date overflow
    pd = cd - one_day
    pd = pd if Entry.objects.exclude(created_at__year=cd.year, 
            created_at__month=cd.month, created_at__day=cd.day).filter(
                                          created_at__lt=cd).exists() else None
    nd = cd + one_day
    nd = nd if Entry.objects.exclude(created_at__year=cd.year, 
            created_at__month=cd.month, created_at__day=cd.day).filter(
                                          created_at__gt=cd).exists() else None

    entry_list = Entry.objects.filter(created_at__year=year, created_at__month=month, created_at__day=day)
    return render_to_response('news/archive.html', 
            {'entry_list': entry_list, 'prev_date': pd, 
                                    'next_date': nd, 'current_date': cd})


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
