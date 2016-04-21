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
    
