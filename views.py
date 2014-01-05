from django.shortcuts import render, Http404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from news.forms import EntryForm
from news.models import Entry
from django.utils.timezone import utc
import datetime

def index(request):
    entry_list = Entry.objects.all()
    return render(request, 'news/index.html', {'entry_list': entry_list})


# TODO: 404 ?

def detail(request, year, month, day, slug):
    try:
        e = Entry.public.get(slug=slug)
    except Entry.DoesNotExist:
        raise Http404
    prev_entry = e.prev_entry()
    next_entry = e.next_entry()
    return render(request, 'news/detail.html', {'entry': e, 'prev_entry': prev_entry, 'next_entry': next_entry})


def day_archive(request, year, month, day):
    cd = datetime.datetime(int(year), int(month), int(day)).replace(tzinfo=utc)
    one_day = datetime.timedelta(days=1)
    # TODO: Test against date overflow
    pd = cd - one_day
    pd = pd if Entry.objects.exclude(created_at__year=cd.year, 
                                     created_at__month=cd.month, 
                                     created_at__day=cd.day).filter(
                                          created_at__lt=cd).exists() else None
    nd = cd + one_day
    nd = nd if Entry.objects.exclude(created_at__year=cd.year, 
                                     created_at__month=cd.month, 
                                     created_at__day=cd.day).filter(
                                          created_at__gt=cd).exists() else None

    entry_list = Entry.objects.filter(created_at__year=year, 
                                      created_at__month=month, 
                                      created_at__day=day)
    return render(request, 'news/day_archive.html', 
                                                    {'entry_list': entry_list, 
                                                     'prev_day': pd,
                                                     'next_day': nd, 
                                                     'current_day': cd
                                                                      })


def month_archive(request, year, month):
    cm = datetime.datetime(int(year), int(month), 1).replace(tzinfo=utc)
    one_day = datetime.timedelta(days=1)

    pm = cm - one_day
    pm = pm if Entry.objects.filter(created_at__lt=cm).exists() else None

    nm = cm + datetime.timedelta(days=31)
    nm = nm if Entry.objects.exclude(created_at__year=cm.year, 
            created_at__month=cm.month).filter(created_at__gt=cm).exists() else None

    entry_list = Entry.objects.filter(created_at__year=year, 
                                      created_at__month=month)
    return render(request, 'news/month_archive.html', 
                                                     {'entry_list': entry_list,
                                                      'prev_month': pm, 
                                                      'next_month': nm,
                                                      'current_month': cm
                                                                             })


def year_archive(request, year):
    cy = datetime.datetime(int(year), 1, 1).replace(tzinfo=utc)
    one_day = datetime.timedelta(days=1)

    py = cy - one_day
    py = py if Entry.objects.filter(created_at__lt=cy).exists() else None

    ny = cy + datetime.timedelta(days=366)
    ny = ny if Entry.objects.exclude(
                                     created_at__year=cy.year).filter(
                                     created_at__gt=cy).exists() else None

    months = {str(month).rjust(2, '0'): None for month in range(1, 13)}
    for month in months:
        months[month] = Entry.objects.filter(created_at__year=cy.year,
                                       created_at__month=month).count()

    return render(request, 'news/year_archive.html', 
                                                    {'months': months,
                                                     'prev_year': py,
                                                     'next_year': ny,
                                                     'current_year': cy
                                                                       })


def form(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/news')
    else:
        form = EntryForm()
    return render(request, 'news/form.html', {'form': form})
