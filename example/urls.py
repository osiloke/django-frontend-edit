from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example app urls:
    url(r'^frontend/', include('frontend.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', include('todo.urls')),
)
