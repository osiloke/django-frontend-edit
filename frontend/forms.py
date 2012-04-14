'''
Created on Mar 6, 2011

@author: osilocks
''' 
from uuid import uuid4

from django import forms
from django.conf import settings

def get_model_form(obj, field_names, \
                    data=None, files=None, parent_model_related_name=None, \
                    parent_model=None, parent_id=None, values=None):
    """
    Returns the in-line addition form for adding a single model field.
    """ 

    #Left over from mezzanine
    try:
        widget_overrides = settings.WIDGET_OVERRIDES
    except AttributeError:
        widget_overrides = {}

    try:
        settings.FORMS_USE_HTML5
    except AttributeError:
        forms_use_html5 = False

    'Default initial values'
    initial={"app": obj._meta.app_label,"model": obj._meta.object_name.lower(),
            "parent_model_related_name":parent_model_related_name,
            "parent_model":parent_model,"parent_id":parent_id, parent_model:parent_id }
    hidden_fields = []

    'get some dynamic values'
    if values:
        obj_fields = [f.name for f in obj._meta.fields] 
        for key in values:
            value = values[key]
            if key in obj_fields:
                initial[key]=value
                if key not in field_names:
                    field_names = "%s,%s"%(field_names, key)
                    'no need to make this field editable since we already have its value'
                    hidden_fields.append(key)
    initial['fields'] = field_names

    class ModelForm(forms.ModelForm):
        """
        In-line form for adding a single model field.
        """

        app = forms.CharField(widget=forms.HiddenInput)
        model = forms.CharField(widget=forms.HiddenInput)
        fields = forms.CharField(widget=forms.HiddenInput)
        parent_model = forms.CharField(required=False,widget=forms.HiddenInput)
        parent_id = forms.CharField(required=False,widget=forms.HiddenInput)
        parent_model_related_name = forms.CharField(required=False,widget=forms.HiddenInput)
            
        class Meta:
            model = obj.__class__
            fields = field_names.split(",")
#
        def __init__(self, *args, **kwargs):
            super(ModelForm, self).__init__(*args, **kwargs)
            self.uuid = str(uuid4())

            for f in self.fields.keys():
                'Make page model content type id a hidden field'
                if parent_model == f: self.fields[f].widget = forms.HiddenInput()
                if f in hidden_fields: self.fields[f].widget = forms.HiddenInput()
                field_class = self.fields[f].__class__
                try:
                    field_type = widget_overrides[field_class]
                except KeyError:
                    pass
                else:
                   self.fields[f].widget = fields.WIDGETS[field_type]()
                css_class = self.fields[f].widget.attrs.get("class", "")
                css_class += " " + field_class.__name__.lower()
                self.fields[f].widget.attrs["class"] = css_class
                self.fields[f].widget.attrs["id"] = "%s" % (f)
                if forms_use_html5 and self.fields[f].required:
                    self.fields[f].widget.attrs["required"] = ""

        def save(self, commit=True):
            obj = super(ModelForm, self).save(commit)
            _parent_model = self.data["parent_model"]
            _parent_rel_field = self.data["parent_model_related_name"]

            #the model needs to be added to the parent model (related field)
            if _parent_model and _parent_rel_field:
                #get related parent field
                parent_field = getattr(self.Meta.model, _parent_rel_field)
                #get instance of parent model
                parent_model = parent_field.related.model.objects.get(id=self.data["parent_id"])

                parent_related_field = getattr(parent_model, parent_field.related.field.name)
                #add model instance to parent
                parent_related_field.add(obj)

            return obj

    return ModelForm(instance=obj, initial=initial, data=data, files=files)

