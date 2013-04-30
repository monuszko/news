from __future__ import division
from news.models import Entry
from django.core.urlresolvers import reverse
from django.shortcuts import render, Http404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from news.forms import CommentForm
from django.utils.timezone import utc
from math import ceil
import datetime

PER_PAGE = 2

def index(request):
    entry_list = Entry.public.all()
    return render(request, 'news/index.html', {'entry_list': entry_list})

def another_page(request, page_number):
    page_number = int(page_number)
    if page_number == 1:
        return HttpResponseRedirect(reverse('news:index'))
    start = (page_number - 1) * PER_PAGE
    entry_list = Entry.public.all()[start:start + PER_PAGE]
    prev_page = next_page = None
    if entry_list:
        prev_page = page_number - 1
        next_page = page_number + 1 if entry_list.reverse()[0].next_entry() else None
    return render(request, 'news/index.html', {'entry_list': entry_list,
                                               'prev_page': prev_page,
                                               'next_page': next_page
                                                                     })


def detail(request, year, month, day, slug):
    try:
        e = Entry.public.filter(created_at__year=year, created_at__month=month,
                                            created_at__day=day).get(slug=slug)
    except Entry.DoesNotExist:
        raise Http404

    comments = e.comment_set.all()
    prev_entry = e.prev_entry()
    next_entry = e.next_entry()
    
    # comment form:
    if request.method == 'POST': 
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.entry = e
            c.save()
    else:
        form = CommentForm()

    return render(request, 'news/detail.html', {'entry': e, 'prev_entry': prev_entry, 'next_entry': next_entry,
        'comments': comments, 'form': form})

# TODO: reimplement using unique_for_date once it's patched


def day_archive(request, year, month, day):
    cd = datetime.datetime(int(year), int(month), int(day)).replace(tzinfo=utc)
    one_day = datetime.timedelta(days=1)
    # TODO: Test against date overflow
    pd = cd - one_day
    pd = pd if Entry.public.exclude(created_at__year=cd.year, 
                                    created_at__month=cd.month, 
                                    created_at__day=cd.day).filter(
                                        created_at__lt=cd).exists() else None
    nd = cd + one_day
    nd = nd if Entry.public.exclude(created_at__year=cd.year, 
                                    created_at__month=cd.month, 
                                    created_at__day=cd.day).filter(
                                        created_at__gt=cd).exists() else None

    entry_list = Entry.public.filter(created_at__year=year, 
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
    pm = pm if Entry.public.filter(created_at__lt=cm).exists() else None

    nm = cm + datetime.timedelta(days=31)
    nm = nm if Entry.public.exclude(created_at__year=cm.year, 
            created_at__month=cm.month).filter(created_at__gt=cm).exists() else None

    day = cm # day as date gives extra flexibility in templates
    days = []
    while day.month== cm.month:
        num_entries = Entry.public.filter(created_at__year=day.year,
                                          created_at__month=day.month,
                                          created_at__day=day.day).count()
        days.append((day, num_entries))
        day += one_day

    return render(request, 'news/month_archive.html', 
                                                     {'days': days,
                                                      'prev_month': pm, 
                                                      'next_month': nm,
                                                      'current_month': cm
                                                                             })


def year_archive(request, year):
    cy = datetime.datetime(int(year), 1, 1).replace(tzinfo=utc)
    one_month = datetime.timedelta(days=31)

    py = cy.replace(year=cy.year-1)
    py = py if Entry.public.filter(created_at__lt=cy).exists() else None

    ny = cy.replace(year=cy.year+1)
    ny = ny if Entry.public.exclude(
                                     created_at__year=cy.year).filter(
                                     created_at__gt=cy).exists() else None


    month = cy # month as date gives extra flexibility in templates
    months = []
    while month.year == cy.year:
        num_entries = Entry.public.filter(created_at__year=month.year,
                                          created_at__month=month.month).count()
        months.append((month, num_entries))
        month += one_month

    return render(request, 'news/year_archive.html', 
                                                    {'months': months,
                                                     'prev_year': py,
                                                     'next_year': ny,
                                                     'current_year': cy
                                                                       })

