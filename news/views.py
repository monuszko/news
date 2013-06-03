from __future__ import division
from math import ceil
from news.models import Entry, Blog
from news.forms import PartialEntryForm
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.shortcuts import render, Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.timezone import utc, now as utcnow
import datetime

PER_PAGE = 10

def index(request, blogname):
    bl = Blog.objects.get(author__username=blogname) #TODO: handle DoesNotExist
    page_number = int(request.GET.get('page', 1))
    entry_list = Entry.public.filter(blog=bl)
    max_page = ceil(entry_list.count() / PER_PAGE)
    start = (page_number - 1) * PER_PAGE
    entry_list = entry_list[start:start + PER_PAGE]
    prev_page = page_number - 1 if 1 < page_number <= max_page else None
    next_page = page_number + 1 if page_number < max_page else None
    return render(request, 'news/index.html', {'blog': bl.author.username,
                                               'username': request.user.username,
                                               'path': request.path,
                                               'entry_list': entry_list,
                                               'prev_page': prev_page,
                                               'next_page': next_page})


@login_required
def post(request, blogname):
    if request.user.username != blogname:
        return HttpResponse("This is not your blog !!")
    if request.method == 'POST':
        form = PartialEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.blog = Blog.objects.get(author__username=blogname)
            entry.save()
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = PartialEntryForm()

    return render(request, 'news/post.html', {'blog': blogname, 
                                              'username': request.user.username,
                                              'path': request.path,
                                              'form': form})


@login_required
def edit(request, blogname, year, month, day, slug):
    if request.user.username != blogname:
        return HttpResponse("This is not your blog !!")
    bl = Blog.objects.get(author__username=blogname)
    try:
        e = Entry.public.filter(blog=bl, created_at__year=year, 
                created_at__month=month, created_at__day=day).get(slug=slug)
    except Entry.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = PartialEntryForm(request.POST, instance=e)
        if form.is_valid():
            if request.POST.get('save'):
                form.save()
                return HttpResponseRedirect(e.get_absolute_url())
            elif request.POST.get('delete'):
                e.delete()
                return HttpResponseRedirect(reverse('news:index', kwargs={'blogname': bl.author.username}))
    else:
        form = PartialEntryForm(instance=e)
    return render(request, 'news/edit.html', {'blog': bl.author.username, 'form': form})

def detail(request, blogname, year, month, day, slug):
    bl = Blog.objects.get(author__username=blogname)
    try:
        e = Entry.public.filter(blog=bl, created_at__year=year, 
                created_at__month=month, created_at__day=day).get(slug=slug)
    except Entry.DoesNotExist:
        raise Http404

    prev_entry = e.prev_entry()
    next_entry = e.next_entry()
    
    return render(request, 'news/detail.html', {'blog': bl.author.username, 'entry': e,
                                                'username': request.user.username,
                                                'path': request.path,
                                                'prev_entry': prev_entry, 
                                                'next_entry': next_entry})

# TODO: reimplement using unique_for_date once it's patched


def day_archive(request, blogname, year, month, day):
    cd = datetime.datetime(int(year), int(month), int(day)).replace(tzinfo=utc)
    today = utcnow().date()
    bl = Blog.objects.get(author__username=blogname)
    earliest = Entry.public.filter(blog=bl).reverse()[0].created_at.date()
    if not today >= cd.date() >= earliest:
        raise Http404
    # TODO: Test against date overflow
    one_day = datetime.timedelta(days=1)
    pd = cd - one_day
    pd = pd if today > pd.date() >= earliest else None
    nd = cd + one_day
    nd = nd if today > nd.date() >= earliest else None

    entry_list = Entry.public.filter(blog=bl, created_at__year=year, 
                                  created_at__month=month, created_at__day=day)

    return render(request, 'news/day_archive.html', 
                                                    {'blog': bl.author.username,
                                                     'username': request.user.username,
                                                     'path': request.path,
                                                     'entry_list': entry_list, 
                                                     'prev_day': pd,
                                                     'next_day': nd, 
                                                     'the_day': cd
                                                                      })


def month_archive(request, blogname, year, month):
    cm = datetime.datetime(int(year), int(month), 1).replace(tzinfo=utc)
    today = utcnow().date().replace(day=1)
    bl = Blog.objects.get(author__username=blogname)
    earliest = Entry.public.filter(blog=bl).reverse()[0].created_at.date()
    earliest = earliest.replace(day=1)
    if not today >= cm.date() >= earliest:
        raise Http404
    one_day = datetime.timedelta(days=1)
    pm = cm - one_day
    pm = pm if Entry.public.filter(blog=bl, created_at__lt=cm).exists() else None

    nm = cm + datetime.timedelta(days=31)
    nm = nm if Entry.public.exclude(blog=bl, created_at__year=cm.year, 
            created_at__month=cm.month).filter(created_at__gt=cm).exists() else None

    day = cm # day as date gives extra flexibility in templates
    days = []
    while day.month== cm.month:
        num_entries = Entry.public.filter(blog=bl,
                                          created_at__year=day.year,
                                          created_at__month=day.month,
                                          created_at__day=day.day).count()
        days.append((day, num_entries))
        day += one_day

    return render(request, 'news/month_archive.html', 
                                                     {'blog': bl.author.username,
                                                      'username': request.user.username,
                                                      'path': request.path,
                                                      'days': days,
                                                      'prev_month': pm, 
                                                      'next_month': nm,
                                                      'current_month': cm
                                                                             })


def year_archive(request, blogname, year):
    bl = Blog.objects.get(author__username=blogname)
    cy = datetime.datetime(int(year), 1, 1).replace(tzinfo=utc)
    today = utcnow().date().replace(day=1, month=1)
    earliest = Entry.public.filter(blog=bl).reverse()[0].created_at.date()
    earliest = earliest.replace(day=1, month=1)
    if not today >= cy.date() >= earliest:
        raise Http404
    one_month = datetime.timedelta(days=31)

    py = cy.replace(year=cy.year-1)
    py = py if Entry.public.filter(blog=bl, created_at__lt=cy).exists() else None

    ny = cy.replace(year=cy.year+1)
    ny = ny if Entry.public.exclude(
                                    created_at__year=cy.year).filter(blog=bl,
                                    created_at__gt=cy).exists() else None


    month = cy # month as date gives extra flexibility in templates
    months = []
    while month.year == cy.year:
        num_entries = Entry.public.filter(blog=bl,
                                          created_at__year=month.year,
                                          created_at__month=month.month).count()
        months.append((month, num_entries))
        month += one_month

    return render(request, 'news/year_archive.html', {'blog': bl.author.username,
                                                      'username': request.user.username,
                                                      'path': request.path,
                                                      'months': months,
                                                      'prev_year': py,
                                                      'next_year': ny,
                                                      'current_year': cy
                                                                        })

