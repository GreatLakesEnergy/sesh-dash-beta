# Import all the neccessary models
from seshdash.models import *

def get_model_from_string(model_name):
    model = eval(model_name)
    return model


""" Returns the first model reference from string """
def get_model_first_reference(model_name, instance):
    # model_name must be a string
   
    model_set_attr = model_name.lower() + '_set' 
    ref = getattr(instance, model_set_attr)
    first_ref = ref.first()
    return first_ref
 
def get_model_fields_names(model):
    """ Returns a list of field names """
    fields = model._meta.fields
    field_names = []

    for field in fields:
        field_names.append(field.name)

    return field_names

def get_model_verbose(model):
    """ Returns a dictionary where keys are columns and values are verbose name """
    fields = model._meta.fields
    
    verbose_dict = {}

    for field in fields:
        verbose_dict[field.name] = field.verbose_name
    
    return verbose_dict

def get_latest_instance(model):
    """ Returns the latest row in a model """
    return model.objects.all().order_by('id').last()



