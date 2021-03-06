from django.template.loader import get_template

# Import django errors
from django.db.utils import OperationalError
# Import all the neccessary models
from seshdash.models import *
from seshdash.data.db.influx import get_latest_point_site
#import wearher data function
from seshdash.api.forecast import ForecastAPI
from seshdash.utils.reporting import _format_column_str
from django.utils import timezone

import logging


logger = logging.getLogger(__name__)

def get_model_from_string(model_name):
    """
    Return a model name froms string
    """
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


def get_model_first_reference(model_name, instance):
    """ Returns the first model reference from string """
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
        return Daily_Data_Point.MEASUREMENTS_VERBOSE_NAMES.get(measurement,measurement)
    except KeyError ,e :
        logger.error(e)
        pass


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


def get_site_measurements(site):
    """
    return measurements of a specific site
    """
    site_measurements = site.site_measurements

    #if no measurements
    if site_measurements is None:
        site.site_measurements = Site_Measurements.objects.create()
        site.save()
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

    logger.debug("Got measurements for site %s"%site_measurements_items)
    return site_measurements_items


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

        return list(set(status_card_items))

    except OperationalError ,e :
        logger.error(e)
        pass
    except Exception  ,e :
        logger.error(e)
        pass


def get_all_associated_sensors(site):
    """
    Returns the associated sensors for
    a given site
    """
    sensors_list = []

    sensors = Sensor_Node.objects.filter(site=site)

    for sensor in sensors:
            sensors_list.append(sensor)

    return sensors_list


def get_config_sensors(sensors):
    """
    Function to generate the configuration for all of the
    sensors
    """
    configuration = ""

    sensor_node_index = 0

    bmv_number = None # Setting the bmv number so that it can be used in the initial bmv config, This is because we can only have on bmv per site


    for sensor in sensors:

           t = get_template('seshdash/configs/sensor_node.conf')
           text = t.render({'number': sensor.node_id, 'sensor_number': (sensor_node_index + 1) })
           sensor_node_index = sensor_node_index + 1

           configuration = configuration + text

    return configuration, 0


def get_quick_status(user_sites):
    """
    returns battery state and future forecast
    """
    #battery rules limits
    battery_limit = Status_Rule.battery_rules.keys()
    battery_limit.sort()

    #weather rules limits
    weather_limit = Status_Rule.weather_rules.keys()
    weather_limit.sort()
    # current time
    now = timezone.now()

    results = []

    #getting latest_points
    for site in user_sites:
        site_dict = {}
        site_dict['site'] = site

        battery_latest_dict = get_latest_point_site(site,'soc')
        if battery_latest_dict is not None:
            battery_latest_point = battery_latest_dict['value']
            #finding battery_voltage color
            if battery_latest_point < battery_limit[0]:
                color = Status_Rule.battery_rules[battery_limit[0]]
                site_dict['battery']= color

            elif battery_latest_point > battery_limit[0] and battery_latest_point < battery_limit[1]:
                color = Status_Rule.battery_rules[battery_limit[1]]
                site_dict['battery'] = color

            else:
                color = Status_Rule.battery_rules[battery_limit[2]]
                site_dict['battery'] = color

        #site weather_data
        site_weather_data = Site_Weather_Data.objects.filter(site= site)
        cloud_cover = []
        for weather_data in site_weather_data:
            cloud_cover.append(weather_data.cloud_cover)
        if len(cloud_cover) is not 0:
            average_cloud_cover = sum(cloud_cover)/len(cloud_cover)

            #finding weather_data color
            if average_cloud_cover < weather_limit[0]:
                color = Status_Rule.weather_rules[weather_limit[0]]
                site_dict['weather'] = color
            else:
                color = Status_Rule.weather_rules[weather_limit[1]]
                site_dict['weather'] = color
        #appending to results list
        results.append(site_dict)

    return results


def associate_sensors_sets_to_site(sensor_sets, site):
    """
    Function to associate sensors sets to site
    """
    for sensor_set in sensor_sets:
        try:
            if sensor_set.is_valid():
                save_sensor_set(sensor_set, site)
        except ValidationError:
            logger.debug("sensor not set for site")


def save_sensor_set(sensor_set, site):
    """
    For saving a set of sensors and a
    associating it with the right site
    """
    for sensor in sensor_set:
        sensor_instance = sensor.save(commit=False)
        sensor_instance.site = site
        sensor.save()


def model_list_to_field_list(model_list, field):
    """
    Convert a model dictionary into a list with the values of the field from each item as each item.

    @params model_list - list of model items
    @params field - name of field to extract from each model
    @returns list with value of field for each model
    """
    result_list = []
    for val in model_list:
        result_list.append(getattr(val,field))

    return result_list


def get_site_sensor_fields(site):
    """
    Returns the name of the fields for a site,
    These are the fields that are stored in influx db

    @param site - The site for which the data has to come from
    """

    fields = []

    # Check if site is VRM or RMC
    if not site.vrm_account:
        sensors = Sensor_Node.objects.filter(site=site)

        for sensor in sensors:
            fields += sensor.get_fields()

    return sorted(list(set(fields))) # removing duplicate values if and sorting


def get_site_sensor_fields_choices(site):
    """
    Returns a dict containing the site fields as the key,
    and a user friendly name as the value
    """
    fields = get_site_sensor_fields(site)
    choices = {}

    for field in fields:
        choices[field] = _format_column_str(field)

    return choices


def get_alert_rule_fields_choices(site):
    """
    This returns alert rule field choices for a given
    site
    """
    fields = get_site_sensor_fields_choices(site)
    fields['RMC_status#minutes_last_contact'] = 'RMC Last Contact'
    return fields

