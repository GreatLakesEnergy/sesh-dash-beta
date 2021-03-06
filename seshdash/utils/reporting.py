from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert,Daily_Data_Point, Sesh_User, Report_Sent
from seshdash.utils.send_mail import send_mail

from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models import Avg, Sum
from django.apps import apps
from django.core.exceptions import FieldError

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

    # Store the report
    report = Report_Sent(
            report_job = report,
            title = subject,
            date = context_dict["date"],
            content = report_data,
            sent_to = map(lambda x: x.email, users),
            status = val
            )
    report.save()

    return val

def get_measurement_unit(measurement):
    """
    Get a unit for measurement or refer to default
    """
    return Daily_Data_Point.UNITS_DICTIONARY.get(measurement,Daily_Data_Point.DEFAULT_UNIT)

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

def get_report_table_attributes(site):
    """
    Returns the report attributes for daily data point
    found in settings
    """
    attributes = get_table_report_dict(site, 'Daily_Data_Point', ['sum', 'average'])
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
    possible_attributes = get_report_table_attributes(report.site)
    data_list = []

    for attribute in possible_attributes:
        data_dict = {}
        if is_in_report_attributes(attribute, report):
            data_dict['status'] = 'on'
        else:
            data_dict['status'] = 'off'

        data_dict['report_value'] = attribute
        data_list.append(data_dict)

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

def is_in_report_attributes_dictionary(dictionary, array_dictionary):
    """
    Checks if a given dictionary is in report table attributes for a given site,
    :param dictionary: The dictionary to check if is in
    :return: Returns boolean True or False basing if the dictionary was found or not
    """

    for item in array_dictionary:
        if item == dictionary:
            return True

    return False

def get_table_report_dict(site, report_table_name, operations):
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

                # Removing values for sites that do not have pv
                if not site.has_pv:
                    if field.name in ['daily_pv_yield', 'daily_power_cons_pv']:
                        continue

                # Removing values for sites that do not have grid
                if not site.has_grid:
                    if field.name in ['daily_grid_outage_n', 'daily_grid_outage_t', 'daily_grid_usage']:
                        continue

                # Removing values for site that do not have batteries
                if not site.has_batteries:
                    if field.name in ['daily_battery_charge']:
                        continue

                report_attribute_dict = {}
                report_attribute_dict['column'] = field.name
                report_attribute_dict['table'] = report_table_name
                report_attribute_dict['operation'] = operation
                report_attribute_dict['user_friendly_name'] = _format_column_str(field.name) + ' ' + operation
                report_table_attributes.append(report_attribute_dict)

    return report_table_attributes
