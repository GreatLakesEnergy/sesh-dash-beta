from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert,Daily_Data_Point, Sesh_User
from seshdash.utils.send_mail import send_mail
from seshdash.utils.model_tools import get_measurement_unit
from seshdash.data.db.kapacitor import Kapacitor
from seshdash.data.db.influx import Influx

from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models import Avg, Sum
from django.apps import apps
from django.core.exceptions import FieldError
from django.conf import settings
from django.template.loader import get_template

from guardian.shortcuts import get_users_with_perms
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import logging
import json

# Instantiating the logger
logger = logging.getLogger()


def send_report(report):
    """
    Sends report to the users with
    activated report permission on the site
    """
    report_data = generate_report_data(report)
    users = Sesh_User.objects.filter(organisation=report.site.organisation, send_mail=True) #users with emailreport on in the organisation
    emails = get_emails_list(users)

    # Collecting the data needed in the email reports.
    subject = report.duration.capitalize() + " report for " + report.site.site_name
    context_dict = {}
    context_dict["title"] = subject
    context_dict["report"] = report
    context_dict["date"] = datetime.now()
    context_dict["report_data"] = report_data
    context_dict["url_to_dash"] = 'http://dash.gle.solar/site/' + report.site.site_name

    val = send_mail(subject, emails, context_dict, 'reporting')
    return val

def generate_report_data(report):
    """
    Function to generate a report,
    The function receives a report model instance and
    it returns a dict containing the aggregated value of the
    report attributes
    """
    report_data = []
    now = datetime.now()

    # Getting the correct date range
    if report.duration == "daily":
        start = now - relativedelta(hours=24)
    elif report.duration == "weekly":
        start = now - relativedelta(weeks=1)
    elif report.duration == "monthly":
        start = now - relativedelta(months=1)


    # Getting the aggregation of the values in the report attributes
    for attribute in report.attributes:
        if "table" in attribute: # If it uses sesh tables
            operation = _get_operation(attribute) # Getting the operation to execute, average or sum

            try:
                table = apps.get_model(app_label="seshdash", model_name=attribute["table"])
            except LookupError:
                raise Exception("ERROR IN REPORTS: Incorrect table name in the report jsonfield")

            try:
                data = table.objects.filter(site=report.site,
                                        date__range=[start, now]).aggregate(val = operation(attribute["column"]))
            except FieldError:
                raise Exception("ERROR IN REPORTS: Incorrect column name in the jsonfield")

            data["user_friendly_name"] =  _format_column_str(attribute["column"]) + " " + attribute["operation"]
            data["unit"] = get_measurement_unit(attribute["column"])
            report_data.append(data)
        else:
            print "About to use influx and kapacitor to get report dtaa"
            report_data = ['TODO: USING INFLUX AND KAPACITOR TO GET REPORT DATA']

    return report_data

def _get_operation(attribute):
    """
    Function to return the operation to be used
    when aggregating data for a report attribute
    """
    if attribute['operation'] == "average":
        operation = Avg
    elif attribute['operation'] == "sum":
        operation = Sum
    else:
        raise Exception("Invalid opperation in attribute for report")

    return operation


def _format_column_str(string):
    """
    This formats a columns string to look
    more user friendly
    """
    mod = ''
    for index, letter in  enumerate(string):
        if letter == '_':
            mod = mod + ' '
        else:
            mod = mod + letter
    return mod.capitalize()


def get_emails_list(users):
    """
    Returns a list of emails from the users
    """
    emails = []

    for user in users:
        emails.append(user.email)

    return emails

def get_report_table_attributes():
    """
    Returns the report attributes for sesh report tables found in settings.
    """

    """
    REMOVING: For now assuming that there are no sesh tables to create report from, only using influx
    from django.conf import settings
    attributes  = []

    for table_name in settings.SESH_REPORT_TABLES:
        attributes.extend(get_table_report_dict(table_name, ['sum', 'average']))

    return attributes
    """
    i = Influx()
    measurements = i.get_measurements()
    attributes = []
    operations = ['sum', 'mean']

    for measurement in measurements:
        if measurement['name'] != 'site':
            for operation in operations:
                dict = {}
                dict['field'] = str(measurement['name'])
                dict['output_field'] = str(operation + '_' + measurement['name'])
                dict['operation'] = str(operation)
                dict['user_friendly_name'] = str(_format_column_str(measurement['name']) + ' ' + operation)
                attributes.append(dict)

    return attributes





def get_report_instance_attributes(report):
    """
    This function takes in a report,
    and then generates a dict representing the elements
    in the json field and the value
    This is to be passed to a template in order to help in editing a report
    """
    data_list = []
    jsondata = report.attributes

    for field in jsondata:
        data_dict = {}
        data_dict['report_value'] = field
        data_dict['status'] = 'on'
        data_list.append(data_dict)

    return data_list


def get_edit_report_list(report):
    """
    Returns a list that represents the status
    of items in the report compared to what can be in the reports
    """
    possible_attributes = get_report_table_attributes()
    data_list = []


    for attribute in possible_attributes:
        data_dict = {}
        if is_in_report_attributes(attribute, report):
            data_dict['status'] = 'on'
        else:
            data_dict['status'] = 'off'

        data_dict['report_value'] = attribute
        data_list.append(data_dict)

    print "The returned data list is: %s" % data_list
    return data_list

def is_in_report_attributes(dictionary, report):
    """
    This function checks if a dictionary of items is
    in the report attributes
    @param dictionary: this is a string containing json reprot data "{'column':'pv_yield', 'table':'Daily_Data_Point', ...}
    @param report: Report class instance
    """
    report_attributes = report.attributes

    for item in report_attributes:
        if item == dictionary:
            return True
    return False


def get_table_report_dict(report_table_name, operations):
    """
    Returns a dict containing all the reporting values
    possible for models containing reporting data

    @param report_table_name: Ex Daily_Data_Point
    @param operations: 'sum' or 'average' or ['sum', 'average']
    """
    operations = operations if isinstance(operations, list) else [operations] # Converting any item that is not a list ot a list
    table = apps.get_model(app_label="seshdash", model_name=report_table_name)

    report_table_attributes = []
    fields = table._meta.fields

    for operation in operations:
        for field in fields:
            if field.name != 'site' and field.name != 'id' and field.name != 'date':
                report_attribute_dict = {}
                report_attribute_dict['column'] = field.name
                report_attribute_dict['table'] = report_table_name
                report_attribute_dict['operation'] = operation
                report_attribute_dict['user_friendly_name'] = _format_column_str(field.name) + ' ' + operation
                report_table_attributes.append(report_attribute_dict)

    return report_table_attributes


"""
Kapacitor report utils
"""
def add_report_kap_tasks(report):
    """
    This function adds tasks for a report to kapacitor
    @param report - The report instance in the database
    """
    kap = Kapacitor()
    t = get_template('seshdash/kapacitor_tasks/aggregate_report.tick')
    attributes = report.attributes

    for attribute in attributes:
        data = {
            'database': settings.INFLUX_DB,
            'operation': attribute['operation'],
            'field': attribute['field'],
            'output_field': attribute['output_field'],
            'duration': '1m',
            'site_id': report.site.id,
        }

        task_name = str(site.site_name + '_' + attribute['operation'] + '_' + attribute['field'])
        dbrps = [{"db": settings.INFLUX_DB, "rp": "autogen"}]
        response = kap.create_task(task_name, t.render(data), task_type='batch', dbrps=dbrps)

    return True
