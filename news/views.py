from __future__ import division
from math import ceil
from news.models import Entry, Blog, CustomPage
from news.forms import PartialEntryForm, PartialCustomPageForm
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.shortcuts import render, Http404, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import utc, now as utcnow
import datetime

ENTRIES_PER_PAGE = 10

def index(request, blogname):
    bl = Blog.objects.get(author__username=blogname) #TODO: handle DoesNotExist
    page_number = int(request.GET.get('page', 1))
    entry_list = Entry.objects.filter(blog=bl)
    max_page = ceil(entry_list.count() / ENTRIES_PER_PAGE)
    start = (page_number - 1) * ENTRIES_PER_PAGE
    entry_list = entry_list[start:start + ENTRIES_PER_PAGE]
    prev_page = page_number - 1 if 1 < page_number <= max_page else None
    next_page = page_number + 1 if page_number < max_page else None
    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/index.html', {'blog': bl.author.username,
                                               'path': request.path,
                                               'entry_list': entry_list,
                                               'custompages': cspages,
                                               'prev_page': prev_page,
                                               'next_page': next_page})


def detail(request, blogname, year, month, day, slug):
    bl = Blog.objects.get(author__username=blogname)
    try:
        e = Entry.objects.filter(blog=bl, created_at__year=year, 
                created_at__month=month, created_at__day=day).get(slug=slug)
    except Entry.DoesNotExist:
        raise Http404

    prev_entry = e.prev_entry()
    next_entry = e.next_entry()
    
    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/detail.html', {'blog': bl.author.username, 'entry': e,
                                                'custompages': cspages,
                                                'path': request.path,
                                                'prev_entry': prev_entry, 
                                                'next_entry': next_entry})
# TODO: reimplement using unique_for_date once it's patched


@login_required
def post(request, blogname):
    bl = Blog.objects.get(author__username=blogname)
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

    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/post.html', {'blog': blogname, 
                                              'custompages': cspages,
                                              'path': request.path,
                                              'form': form})


@login_required
def edit_entry(request, blogname, year, month, day, slug):
    bl = Blog.objects.get(author__username=blogname)
    if request.user.username != blogname:
        return HttpResponse("This is not your blog !!")
    try:
        e = Entry.objects.filter(blog=bl, created_at__year=year, 
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

    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/edit.html', {'blog': bl.author.username, 
                                              'custompages': cspages,
                                              'form': form})


def custom_page(request, blogname, page):
    bl = Blog.objects.get(author__username=blogname) #TODO: handle DoesNotExist
    cs = get_object_or_404(CustomPage, blog=bl, url=page)
    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/custompage.html', {'blog': bl.author.username,
                                                    'path': request.path,
                                                    'custompages': cspages,
                                                    'custompage': cs})

# TODO: Dwa razy zapomnialem cos w zwiazku z 'User'

@login_required
def create(request, blogname):
    bl = Blog.objects.get(author__username=blogname) #TODO: handle DoesNotExist
    if request.user.username != blogname: # complicates class-based views
        return HttpResponse("This is not your blog !!")
    if request.method == 'POST':
        form = PartialCustomPageForm(request.POST)
        if form.is_valid(): #TODO: disallow pages like /create/, /2013/,...
            page = form.save(commit=False) #^ choose: /page/ or page ?
            page.blog = Blog.objects.get(author__username=blogname)
            page.save()
            return HttpResponseRedirect(page.get_absolute_url())
    else:
        form = PartialCustomPageForm()

    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/post.html', {'blog': blogname, 
                                              'custompages': cspages,
                                              'path': request.path,
                                              'form': form})

#TODO: template context processors
@login_required
def edit_page(request, blogname, page):
    if request.user.username != blogname:
        return HttpResponse("This is not your blog !!")
    bl = Blog.objects.get(author__username=blogname)
    try:
        cs = CustomPage.objects.get(blog=bl, url=page)
    except CustomPage.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = PartialCustomPageForm(request.POST, instance=cs)
        if form.is_valid():
            if request.POST.get('save'):
                form.save()
                return HttpResponseRedirect(cs.get_absolute_url())
            elif request.POST.get('delete'):
                cs.delete()
                return HttpResponseRedirect(reverse('news:index', kwargs={'blogname': bl.author.username}))
    else:
        form = PartialCustomPageForm(instance=cs)
    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/edit.html', {'blog': bl.author.username, 
                                              'custompages': cspages,
                                              'form': form})


def day_archive(request, blogname, year, month, day):
    cd = datetime.datetime(int(year), int(month), int(day)).replace(tzinfo=utc)
    today = utcnow().date()
    bl = Blog.objects.get(author__username=blogname)
    earliest = Entry.objects.filter(blog=bl).reverse()[0].created_at.date()
    if not today >= cd.date() >= earliest:
        raise Http404
    # TODO: Test against date overflow
    one_day = datetime.timedelta(days=1)
    pd = cd - one_day
    pd = pd if today > pd.date() >= earliest else None
    nd = cd + one_day
    nd = nd if today > nd.date() >= earliest else None

    entry_list = Entry.objects.filter(blog=bl, created_at__year=year, 
                                  created_at__month=month, created_at__day=day)
    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/day_archive.html', 
                                                    {'blog': bl.author.username,
                                                     'custompages': cspages,
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
    earliest = Entry.objects.filter(blog=bl).reverse()[0].created_at.date()
    earliest = earliest.replace(day=1)
    if not today >= cm.date() >= earliest:
        print(today, cm.date(), earliest)
        raise Http404
    one_day = datetime.timedelta(days=1)
    pm = cm - one_day
    pm = pm if Entry.objects.filter(blog=bl, created_at__lt=cm).exists() else None

    nm = cm + datetime.timedelta(days=31)
    nm = nm if Entry.objects.exclude(blog=bl, created_at__year=cm.year, 
            created_at__month=cm.month).filter(created_at__gt=cm).exists() else None

    day = cm # day as date gives extra flexibility in templates
    days = []
    while day.month== cm.month:
        num_entries = Entry.objects.filter(blog=bl,
                                          created_at__year=day.year,
                                          created_at__month=day.month,
                                          created_at__day=day.day).count()
        days.append((day, num_entries))
        day += one_day

    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/month_archive.html', 
                                                     {'blog': bl.author.username,
                                                      'custompages': cspages,
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
    earliest = Entry.objects.filter(blog=bl).reverse()[0].created_at.date()
    earliest = earliest.replace(day=1, month=1)
    if not today >= cy.date() >= earliest:
        raise Http404
    one_month = datetime.timedelta(days=31)

    py = cy.replace(year=cy.year-1)
    py = py if Entry.objects.filter(blog=bl, created_at__lt=cy).exists() else None

    ny = cy.replace(year=cy.year+1)
    ny = ny if Entry.objects.exclude(
                                    created_at__year=cy.year).filter(blog=bl,
                                    created_at__gt=cy).exists() else None


    month = cy # month as date gives extra flexibility in templates
    months = []
    while month.year == cy.year:
        num_entries = Entry.objects.filter(blog=bl,
                                          created_at__year=month.year,
                                          created_at__month=month.month).count()
        months.append((month, num_entries))
        month += one_month

    cspages = CustomPage.objects.filter(blog=bl)
    return render(request, 'news/year_archive.html', {'blog': bl.author.username,
                                                      'custompages': cspages,
                                                      'path': request.path,
                                                      'months': months,
                                                      'prev_year': py,
                                                      'next_year': ny,
                                                      'current_year': cy
                                                                        })

