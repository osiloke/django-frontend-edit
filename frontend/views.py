'''
Created on Mar 6, 2011

@author: osilocks
'''
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.db.models import get_model
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from utilities import check_permission, LazyEncoder
from forms import get_model_form

from frontend.utilities import ajax_view, view_can

from example.someapp.models import MyModel

json_serializer = LazyEncoder()

@ajax_view()
@view_can(MyModel, action="add", ajax=True)
def add(request):
    """
    Process the add form.
    """
    model = get_model(request.POST["app"], request.POST["model"])
    obj = model()
    form = get_model_form(obj, request.POST["fields"], data=request.POST,\
                        files=request.FILES, parent_model_related_name=request.POST["parent_model_related_name"],\
                        parent_model=request.POST["parent_model"], \
                        parent_id = request.POST["parent_id"])

    if form.is_valid():

        saved_obj=form.save()

        'Create change message'
        try:
            model_admin = ModelAdmin(model, admin.site)
            message = model_admin.construct_change_message(request, form, None)
            model_admin.log_change(request, saved_obj, message)
        except Exception:
            pass
        data = {
            'id': saved_obj.id,
            'valid': True,
        }
    else:
        "from django_ajax_validation"
        errors = form.errors
        formfields = dict([(fieldname, form[fieldname]) for fieldname in form.fields.keys()]) 
        final_errors = {}
        for key, val in errors.iteritems():
            if '__all__' in key:
                final_errors[key] = val
            else:# not isinstance(formfields[key].field):
                html_id = formfields[key].field.widget.attrs.get('id') or formfields[key].auto_id
                html_id = formfields[key].field.widget.id_for_label(html_id)
                final_errors[html_id] = val
        data = {
            'valid': False,
            'errors': final_errors,
        }
    return data

add = require_POST(add)

@ajax_view()
@view_can(MyModel, action="change", ajax=True)
def edit(request):
    """
    Process the inline editing form.
    """
    model = get_model(request.POST["app"], request.POST["model"])
    obj = model.objects.get(id=request.POST["id"])
    form = get_model_form(obj, request.POST["fields"], data=request.POST,
                         files=request.FILES)
    if form.is_valid():
        form.save()
        model_admin = ModelAdmin(model, admin.site)
        message = model_admin.construct_change_message(request, form, None)
        model_admin.log_change(request, obj, message)
        data = {
            'valid': True
        }
    else:
        "from django_ajax_validation"
        errors = form.errors
        formfields = dict([(fieldname, form[fieldname]) for fieldname in form.fields.keys()])
#        pprint (errors)
        final_errors = {}
        for key, val in errors.iteritems():
            if '__all__' in key:
                final_errors[key] = val
            elif not isinstance(formfields[key].field):
                html_id = formfields[key].field.widget.attrs.get('id') or formfields[key].auto_id
                html_id = formfields[key].field.widget.id_for_label(html_id)
                final_errors[html_id] = val
        data = {
            'valid': False,
            'errors': final_errors,
        }

    return data

def _handle_cancel(request, instance=None):
    '''
    Handles clicks on the 'Cancel' button in forms. Returns a redirect to the
    last page, the user came from. If not given, to the detail-view of
    the object. Last fallback is a redirect to the common success page.
    '''
    if request.POST.get('submit') == '_cancel':
        if request.GET.get('next', False):
            return HttpResponseRedirect(request.GET.get('next'))
        if instance and hasattr(instance, 'get_absolute_url'):
            return HttpResponseRedirect(instance.get_absolute_url())
#        return HttpResponseRedirect(reverse('frontendadmin_success'))
    return None

@view_can(MyModel, action="delete")
def delete(request, app_label, model_name, instance_id):
     # Check for permission to add/change/delete this object
    if not check_permission(request, "delete", app_label, model_name):
        return HttpResponseForbidden('You have no permission to do this!')

    try:
        model = get_model(app_label, model_name)
    # Model does not exist
    except AttributeError:
        return HttpResponseForbidden('This model does not exist!')
    # get the model and delete it
    model_instance = model.objects.get(pk=instance_id)
    model_instance.delete()
    if request.is_ajax():
        return HttpResponse(json_serializer.encode({'valid':True}), mimetype='application/json')
    else:
        if request.GET.get('next', False):
            return HttpResponseRedirect(request.GET.get('next'))