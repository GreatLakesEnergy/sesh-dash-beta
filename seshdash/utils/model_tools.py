# Import all the neccessary models
from seshdash.models import *
from seshdash.models import Sesh_Site

def get_model_from_string(model_name):
    model = eval(model_name)
    return model


def get_measurement_from_rule(rule):
    """
    Return the name of the measurement from 
    the Alert_Rule checkfield
    """
    if len(rule.check_field.split('#')) == 2:
        model, measurement = rule.check_field.strip().split('#')
        return measurement
    elif len(rule.check_field.split('#')) == 1:
        return rule.check_field



""" Returns the first model reference from string """
def get_model_first_reference(model_name, instance):
    # model_name must be a string
  
    """ 
    model_set_attr = model_name.lower() + '_set' 
    ref = getattr(instance, model_set_attr)
    first_ref = ref.first()
    return first_ref
    """

    model = eval(model_name)
    point = model.objects.filter(id=instance.point_id).first()
    return point
   
 
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



def get_measurement_verbose_name(measurement):
    return Daily_Data_Point.MEASUREMENTS_VERBOSE_NAMES[measurement]


def get_measurement_unit(measurement):
    return Daily_Data_Point.UNITS_DICTIONARY[measurement]
