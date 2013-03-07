from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/$', login, {'template_name': 'accounts/login.html'}),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
