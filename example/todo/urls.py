from django.views.generic import ListView
from django.conf.urls.defaults import patterns

from todo.models import TodoItem

urlpatterns = patterns('',
    (r'^$', ListView.as_view(
        model=TodoItem,
    )),
)