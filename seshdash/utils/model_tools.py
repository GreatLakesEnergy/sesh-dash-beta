# Import django errors
from django.db.utils import OperationalError

# Import all the neccessary models
from seshdash.models import *

import logging

logger = logging.getLogger(__name__)

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
    try:
        return Daily_Data_Point.MEASUREMENTS_VERBOSE_NAMES[measurement]
    except KeyError ,e :
        logger.error(e)
        pass


def get_measurement_unit(measurement):
    return Daily_Data_Point.UNITS_DICTIONARY[measurement]


def get_model_field_names(model):
    """
    This function returns the field names of fields
    in a given model
    """
    fields = model._meta.get_fields()

    field_arr = []

    for field in fields:
        field_arr.append(field.name)

    return field_arr


def get_status_card_items(site):
    """
    Returns the list of items to be displayed in the status card
    The items are the values of all the rows in the status card table that
    contain characters
    """
    try:
        status_card = site.status_card

        if not status_card:
            logger.error('No status card linked to the site')
            return []

        # Getting all the status card fields
        status_card_fields = Status_Card._meta.get_fields()
        status_card_items = []
        # Getting the status card field values, Constructing the arr of the status card items of the site
        for field in status_card_fields:
            status_card_items.append(getattr(status_card, field.name))
        # removing the non char items from the arr
        for i, item in enumerate(status_card_items):
            if type(item) != unicode:
                status_card_items.pop(i)

        # Removing the int items the int item
        for i, item in enumerate(status_card_items):
            if type(item) == int or type(item) == long:
                status_card_items.pop(i)

        return status_card_items
    except OperationalError ,e :
        logger.error(e)
        pass
    except Exception  ,e :
        looger.error(e)
        pass

def get_site_measurements(site):

    site_measurements = site.site_measurements
    # getting all measurement fields
    site_measurements_fields = site_measurements._meta.get_fields()
    site_measurements_items = []
    for field in site_measurements_fields:
        site_measurements_items.append(getattr(site_measurements, field.name))

    #removing non char items
    for i,item in enumerate(site_measurements_items):
        if type(item) != unicode:
            site_measurements_items.pop(i)

    #removing int items
    for i, item in enumerate(site_measurements_items):
        if type(item) == int or type(item) == long:
            site_measurements_items.pop(i)

    return site_measurements_items


def associate_sensors_to_site(sensors_list, site):
    """
    This associates a list of sensors to a 
    a given site
    """
    for sensor in sensors_list:
        if sensor == 'Emon Tx':
            sensor_instance = Sensor_EmonTx.objects.create(site=site)
        elif sensor == 'Emon Th':
            sensor_instance = Sensor_EmonTh.objects.create(site=site)
        elif sensor == 'BMV':
            sensor_instance = Sensor_BMV.objects.create(site=site)


def get_associated_sensors(site):
    """
    Returns the associated sensors for
    a given site
    """
    sensors_list = []
    
    for model in [Sensor_EmonTx, Sensor_EmonTh, Sensor_BMV]:
        sensors = model.objects.filter(site=site)

        for sensor in sensors:
            sensors_list.append(sensor)

    return sensors_list
