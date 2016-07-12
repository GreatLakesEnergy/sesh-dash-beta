# Import django errors
from django.db.utils import OperationalError
# Import all the neccessary models
from seshdash.models import *
from seshdash.data.db.influx import get_latest_point_site
#import wearher data function
from seshdash.api.forecast import ForecastAPI

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
    """
    return measurements of a specific site
    """
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

def get_quick_status(sites):
    """
    returns battery state and future forecast
    """
    key = "8eefab4d187a39b993ca9c875fef6159"

    #battery rules limits
    battery_limit = Status_Rule.battery_rules.keys()
    battery_limit.sort()

    #weather rules limits
    weather_limit = Status_Rule.weather_rules.keys()
    weather_limit.sort()

    results = []

    #getting latest_points
    for site in sites:
        site_dict = {}

        site_dict['site'] = site
        #site coordinates
        lat = site.position.latitude
        lng = site.position.longitude

        #forecast instance
        instance = ForecastAPI(key,lat,lng)

        weather_data = instance.get_7_day_cloudCover()
        weather_data_values = weather_data.values()
        average_weather_data = sum(weather_data_values)/len(weather_data_values)

        battery_latest_dict = get_latest_point_site(site,'battery_voltage')
        battery_latest_point = int(battery_latest_dict['value'])

        #finding battery_voltage color
        if battery_latest_point in range(0,battery_limit[0]):
            color = Status_Rule.battery_rules[battery_limit[0]]
            site_dict['battery']= color

        elif battery_latest_point in range(battery_limit[0],battery_limit[1]):
            color = Status_Rule.battery_rules[battery_limit[1]]
            site_dict['battery'] = color

        else:
            color = Status_Rule.battery_rules[battery_limit[2]]
            site_dict['battery'] = color

        #finding weather_data color
        if average_weather_data < weather_limit[0]:
            color = Status_Rule.weather_rules[weather_limit[0]]
            site_dict['weather'] = color
        else:
            color = Status_Rule.weather_rules[weather_limit[1]]
            site_dict['weather'] = color
        #appending to results list
        results.append(site_dict)

    return results
