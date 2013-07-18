__author__ = 'christian'

from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^projects$', views.ProjectListView.as_view(), name='project_list'),
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'projectroom/login.html'}, name="pr_login"),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'template_name': 'projectroom/logout.html'}, name="pr_logout"),
    #url(r'^(?P<slug>[-\w]+)/$', views.ProjectDetailView.as_view(), name='project'),
    url(r'^(?P<project__slug>[-\w]+)/jobs$', views.JobListView.as_view(), name='job_list'),
    url(r'^(?P<project__slug>[-\w]+)/job/(?P<pk>[\d]+)$', views.JobDetailView.as_view(), name='job'),
    url(r'^(?P<project__slug>[-\w]+)/job/(?P<pk>[\d]+)/edit$', views.JobUpdateView.as_view(), name='job_edit'),
    url(r'^(?P<project__slug>[-\w]+)/job/(?P<pk>[\d]+)/add', views.TicketCreateView.as_view(), name='ticket_add'),
    url(r'^(?P<project__slug>[-\w]+)/job/(?P<job__pk>[\d]+)/ticket/(?P<pk>[\d]+)$', views.TicketDetailView.as_view(), name='ticket'),
    url(r'^(?P<project__slug>[-\w]+)/job/(?P<job__pk>[\d]+)/ticket/(?P<pk>[\d]+)/add$', views.TicketItemCreateView.as_view(), name='ticketitem_add'),
    #(r'^js/(?P<script>[-\w]+)\.js', 'finance.views.js'),
    #(r'^json/', 'finance.views.json')
    #(r'^json/(?P<action>[-\w]+)/$', 'finance.views.json'),
    #url(r'^portal\.js', 'arp_portal.views.portal_js', name="portal_js"),
    #url(r'^grid\.js', 'arp_portal.views.portal_grid', name="portal_grid"),
    #url(r'^portal/usermenu/', 'arp_portal.views.usermenu', name="portal_usermenu"),
    #url(r'^portal/posts/', 'arp_portal.views.posts', name="portal_posts"),
    #url(r'^portal/users/', 'arp_portal.views.userlist', name="portal_userlist")
    #(r'^articles/(\d{4})/$', 'news.views.year_archive'),
    #(r'^articles/(\d{4})/(\d{2})/$', 'news.views.month_archive'),
    #(r'^articles/(\d{4})/(\d{2})/(\d+)/$', 'news.views.article_detail'),
)
