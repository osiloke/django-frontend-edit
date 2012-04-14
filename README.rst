OVERVIEW
========= 
:Author: Osi Emoekpere (http://osiloke.blogspot.com, http://twitter.com/osilocks)

:info: This app provide's full frontend editing functions for models. It can be used to easily update or add models from the frontend of your application. It is spawn from mezzanines frontend editing code.

Requirements
============
mezzanine >= 1.0 (I'm not sure if 1.0 is backwards compatible)
django-classy-tags

METHODOLOGY
===========

Setup
=====
Add the frontend app to your installed apps after all mezzanine apps in your ``settings.py``::

   INSTALLED_APPS = (
       ...
       'frontend',
       ...
   )

In template files where you would want to provide editing functions, include the frontend template tag library


You can provide add functions for a model by using the following tag format::

    {%  can_add [model_obj] [model_fields] %}{% endcan_add %}

The `model_obj` can be an actual model object or a list of model objects, useful if you don't want to pass an extra model_obj template variable in addition to a list of your objects (It's just for convenience). `model_fields` are the fields which can be modified. 

An example would be::
    
    {% can_add image name image description %} 
        ... any html ...
    {% endcan_add %}


TODO
====
* Create a general modify tag which provides all modify functions i.e add, edit, delete