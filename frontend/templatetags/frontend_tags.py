
'''
Created on Mar 6, 2011

Most of my code is inspired by django mezzanine
@author: osilocks
'''
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db.models.base import Model
from django.template import Context
from django.template.loader import get_template
from django import template
from django.core.urlresolvers import reverse

from frontend.utilities import  checkObjectFields, can
from frontend.forms import get_model_form
 
from classytags.core import Tag, Options
from classytags.arguments import Argument, MultiKeywordArgument, MultiValueArgument, KeywordArgument
from classytags.helpers import InclusionTag

import logging


register = template.Library()

logger = logging.getLogger(__name__)


class can_add(Tag):
    """
    {% can_add [model_name] fields using field=value %}
    """
    name = 'can_add'
    options = Options(
        Argument('model', resolve=False,required=True),
        MultiValueArgument('fields', resolve=False, required=False),
        'using',
        MultiKeywordArgument('values', resolve=True, required=False),
        'params',
        KeywordArgument('parent', resolve=True, required=False),
        KeywordArgument('action', required=False),
        KeywordArgument('template', required=False),
        blocks=[
            ('endcan_add', 'nodelist')
        ]
    )

    def render_tag(self, context, **kwargs):
        def value_ids(values):
            "returns the ids of the values needed to populate the model form"
            parsed_values = {}
            for key in values:
                value = values[key]
                if isinstance(value, Model):
                    parsed_values[key] = value.id
                else:
                    parsed_values[key] = value
            return parsed_values

        def parse_model(model):
            field = model.split(".")
            obj = context[field.pop(0)]

            parent_model = None
            parent_model_field_name_for_object = None
            while field:
                if isinstance(obj, dict) or isinstance(obj,list):
#                if hasattr(obj, "__iter__") and len(obj) > 0:
                    """
                    Fix to ignore parent object if it is a list or tuple
                    A list cannot be the parent of a django model or field so we reset the obj and try with next field
                    """
                    obj = obj[field.pop(0)]
                    obj = obj.__class__
                    parent_model = None
                else:
                    parent_model = obj
                    next_field=field.pop(0)
                    obj = getattr(obj, next_field)
                    if hasattr(obj, "model"):
                        obj = obj.model
                    try:
                        parent_model_field_name_for_object = parent_model._meta.get_field_by_name(next_field)[0]
                    except:
                        pass
            return obj, parent_model, parent_model_field_name_for_object

        model = kwargs.get("model", None)
        nodelist = kwargs.get('nodelist', None)
        parsed = nodelist.render(context)

        fields = kwargs.get('fields', None)
        values = kwargs.get('values', None)

        parent_model_name = None
        parent_model_id = None
        parent_model_related_name = None

        model, parent_model, parent_model_field_name_for_object = parse_model(model)

        if parent_model:
            parent_model_name = parent_model._meta.module_name
            parent_model_id = parent_model.id
            try:
                parent_model_related_name = parent_model_field_name_for_object.related_query_name()
            except Exception, e:
                raise e

        #If model is a related manager, get the model object
        if hasattr(model, "model"):
            model = model.model
        #if model is a collection, get first object
        elif hasattr(model, "__iter__") and len(model) > 0:
            model = model[0]
        if fields and model:
            field_names = ",".join([f for f in fields])
            if can('add', model, context["user"]):
                'Assign page to new content model'
                if not isinstance(model, Model):
                    content_model = model()
                else:
                    content_model = model.__class__()
                context["form"] = get_model_form(content_model, field_names, \
                                 values=value_ids(values), \
                                 parent_model=parent_model_name, \
                                 parent_model_related_name=parent_model_related_name, \
                                 parent_id=parent_model_id )

                context["original"] = parsed
                context["add_text"] = model._meta.verbose_name.title()
                #you can provide a different action for the form to submit to

                try:
                    action = kwargs.get("action", None)
                    context["action"] = action["action"]
                except KeyError:
                    context["action"] = reverse("frontend_add")
                t = get_template("frontend/addable_form.html")
                return t.render(Context(context))
        return parsed

register.tag(can_add)

class can_delete(InclusionTag):
    name = 'can_delete'
    template = 'frontend/deleteable_link.html'
    options = Options( Argument('obj'), Argument('label',required=False, resolve=False), )
    def get_context(self, context, obj, label=None):
         # Check if `model_object` is a model-instance
        if not isinstance(obj, Model):
            raise template.TemplateSyntaxError, "'%s' argument must be a model instance" % obj
        app_label = obj._meta.app_label
        model_name = obj._meta.module_name
        template_context = {
            'delete_link': reverse('frontend_delete', kwargs={
                'app_label': app_label,
                'model_name': model_name,
                'instance_id': obj.pk,
            }),
            'next_link': context['request'].META['PATH_INFO'],
            'label': label,
        }
        # Check for permission
        if can('delete',obj, context["request"]):
            template_context['has_permission'] = True
        context.update(template_context)
        return context
register.tag(can_delete)

def django_model_has_field(model_class, field_name):
    return field_name in model_class._meta.get_all_field_names()


# class frontend_loader(InclusionTag):
#     """
#     Set up the required JS/CSS for the in-line editing toolbar and controls.
#     """  
#     template = 'frontend/loader.html'

#     def get_context(self, context):
#         return {'user': context['user']}

# register.tag(frontend_loader)

@register.inclusion_tag('frontend/loader.html', takes_context=True)
def frontend_loader(context):
    return context