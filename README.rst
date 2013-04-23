Simple news site
++++++++++++++++

Description
===========

An application written for Django1.4.5 using Python2.7.

Pages:
  * *news/* - displays stories sorted by date of creation page. "Read More"
    links are generated, with total length and number of comments 
  * *news/2013/04/12/Joel-is-a-slug* - this format is used for individual
    stories. Contains a form for content submission, links to next/previous
    story and day archive.  * *news/2014/02/17* - day archive, with links to
    next/previous day and month archive.
  * *news/2014/02/* - month archive, with links to next/previous month and year
    archive.
  * *news/2014/* - year archive (a list of months), with links to next/previous
    years.

Example templates included in the templates/ subdirectory. Basic admin
interface available.

Quickstart
==========

1. Add "news" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'news',
      )

2. Include the news URLconf in your project urls.py like this::

      url(r'^news/', include('news.urls')),

3. Run `python manage.py syncdb` to create the news models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
  to create entries (you'll need the Admin app enabled).

Contact
=======

marek.onuszko@gmail.com
