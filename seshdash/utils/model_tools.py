# Import all the neccessary models
from seshdash.models import RMC_status, BoM_Data_Point

def get_model_from_string(model_name):
    model = eval(model_name)
    return model
    
