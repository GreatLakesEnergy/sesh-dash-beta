from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert,Daily_Data_Point, Sesh_User
from seshdash.utils.send_mail import send_mail
from seshdash.utils.model_tools import get_measurement_unit

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
