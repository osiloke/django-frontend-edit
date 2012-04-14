'''
@author: osilocks
'''

from django.conf.urls.defaults import *
from django.contrib import admin 

urlpatterns = []

urlpatterns += patterns("frontend.views",
    url("^add/$", "add", name="frontend_add"),
    url("^edit/$", "edit", name="frontend_edit"),
    url("^delete/(?P<app_label>[\w]+)/(?P<model_name>[\w]+)/(?P<instance_id>[\d]+)/$","delete",name="frontend_delete"),
)