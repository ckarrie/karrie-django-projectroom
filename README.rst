======================
Django projectroom app
======================

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Get Source-Code

      hg clone https://bitbucket.org/ckarrie/karrie-django-projectroom

2. Install requirements with pip::

    pip install -e karrie-django-projectroom
    pip install git+https://github.com/django-mptt/django-mptt.git
    pip install git+https://github.com/brack3t/django-braces.git

3. Add "jobs" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'projectroom',
          'mptt',
      )

4. Include the simplegeo URLconf in your project urls.py like this::

      url(r'^projectroom/', include('projectroom.urls')),

5. Run `python manage.py syncdb` to create the 'projectroom' models.

6. Start the development server and visit http://127.0.0.1:8000/admin/
   to create projectroom (you'll need the Admin app enabled).

7. Visit http://127.0.0.1:8000/jobsprojectroomto manage your jobs.

