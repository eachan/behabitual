from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

import apps.accounts.views
import apps.homepage.views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', TemplateView.as_view(template_name='homepage/home.html'), name='homepage'),
    url(r'^$', apps.homepage.views.HomepageView.as_view(), name='homepage'),
    url(r'^logout/$', apps.accounts.views.LogoutView.as_view(), name='logout'),
    url(r'^password-change/$', apps.accounts.views.password_change, name='password_change'),
    url(r'^password-change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'apps.accounts.views.password_reset_confirm',
        {'post_reset_redirect': '/'},
        name='password_reset_confirm'),
    url(r'^_;', include('apps.autologin.urls')),

) + patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^accounts/forgot/$', 'password_reset', name='account-forgotten'),
    url(r'^accounts/forgot/done/$', 'password_reset_done'),
    
    url(r'^styletile$', TemplateView.as_view(template_name='styles/tile.html'), name='styletile'),
    url(r'^add-trigger$', TemplateView.as_view(template_name='styles/add_trigger.html'), name='add-trigger-placeholder'),
)

from apps.monitoring import *
