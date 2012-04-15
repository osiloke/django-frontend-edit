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

json_serializer = LazyEncoder()

@ajax_view()
def add(request):
    """
    Process the add form.
    """
    model = get_model(request.POST["app"], request.POST["model"])
    if not can("add", model, request.user):
        return {"valid": True, "permissionerror":"You don't have permission to add!"}
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
def edit(request):
    """
    Process the inline editing form.
    """
    try:
        model = get_model(request.POST["app"], request.POST["model"])
        if not can("change", model, request.user):
            return {"valid": True, "permissionerror":"You don't have permission to edit!"}
        obj = model.objects.get(id=request.POST["id"])
        form = get_model_form(obj, request.POST["fields"], data=request.POST,
                             files=request.FILES)
    except Exception:
        pass
        
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

def delete(request, app_label, model_name, instance_id):
     # Check for permission to add/change/delete this object
    

    try:
        model = get_model(app_label, model_name)
        if not can("delete", model, request.user):
            return HttpResponseForbidden('You have no permission to delete!')
    # Model does not exist
    except AttributeError:
        return HttpResponseForbidden('You cannot modify this item')
    # get the model and delete it
    model_instance = model.objects.get(pk=instance_id)
    model_instance.delete()
    if request.is_ajax():
        return HttpResponse(json_serializer.encode({'valid':True}), mimetype='application/json')
    else:
        if request.GET.get('next', False):
            return HttpResponseRedirect(request.GET.get('next'))