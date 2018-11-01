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
    pip install django-mptt-nomagic
    pip install django-braces

3. Add "projectroom" and "mptt" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'projectroom',
          'mptt',
      )

4. Include the simplegeo URLconf in your project urls.py like this::

      url(r'^projectroom/', include('projectroom.urls')),

5. Run `python manage.py migrate` to create the 'projectroom' models.

6. Start the development server and visit http://127.0.0.1:8000/admin/
   to create projectroom (you'll need the Admin app enabled).

7. Visit http://127.0.0.1:8000/db/ manage your jobs.


First Steps / Erste Schritte (DE)
---------------------------------

1. Firma (Auftraggeber) anlegen: /db/projectroom/company/add/
2. Zuordnung Person zu Firma: /db/projectroom/person/add/
3. Projekt anlegen: /db/projectroom/project/add/

    Personen mit Lesezugriff (Read ACL) auswählen
    Personen mit Schreibzugriff (Write ACL) auswählen

4. Stundensatz anlegen: /db/projectroom/rate/
5. Projektkonto anlegen: /db/projectroom/account/
