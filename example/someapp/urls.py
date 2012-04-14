from django.views.generic import ListView
from django.conf.urls.defaults import patterns

from example.someapp.models import MyModel

urlpatterns = patterns('',
    (r'^$', ListView.as_view(
        model=MyModel,
    )),
)