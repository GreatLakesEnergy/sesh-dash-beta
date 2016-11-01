from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert,Daily_Data_Point
from seshdash.utils.send_mail import send_mail

from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models import Avg,Sum
from django.apps import apps

from guardian.shortcuts import get_users_with_perms
from datetime import datetime
from datetime import timedelta
import logging

# Instantiating the logger
logger = logging.getLogger()

# Sends an email of reporting data on past duration


def prepare_report(site, duration="week"):
    """
    Get aggregate data points for the given duration
    duration options are "1w","1m"
    TODO make this date parsing part of time utils class
    Duration: should be "week", "month", "day"

    """
    recipients = []
    cash_power_cost = 220

    now = datetime.date(datetime.now())
    #TODO  This is terrible make decent date parser!
    if duration == 'week':
        date_range = now - timedelta(days=7)
    elif duration == 'month':
        date_range = now - timedelta(days=31)
    else:
        duration = "dai"
        date_range = now - timedelta(hours=24)

    # Query for Daily data points and aggregate across the given time

    print "reports: getting aggregate between  %s and %s" %(date_range,now)
    test =  Daily_Data_Point.objects.filter(site=site, date__range= (date_range,now))
    print "test %s"%test

    aggeragete_data = Daily_Data_Point.objects.filter(site=site,
            date__range= [date_range,now]).aggregate(
                    total_pv = Sum('daily_pv_yield')/1000,
                    total_consumption = Sum('daily_power_consumption_total')/1000,
                    grid_used  = Sum('daily_grid_usage')/1000,
                    grid_outage = Sum('daily_grid_outage_n'),
                    no_alarms = Sum('daily_no_of_alerts'),
                    average_daily_pv = Avg('daily_pv_yield')/1000,
                    average_consumption = Avg('daily_power_consumption_total')/1000,
                    average_daily_grid = Avg('daily_grid_usage')/1000,
                    )

    print "Generating report %s" %(aggeragete_data)
    # Get Users for site
    users = get_users_with_perms(site)
    for user in users:
        recipients.append(user.email)
    logger.debug("emailing %s" %recipients)

    # Add in meta
    subject = "%sly energy usage for %s"%(duration,site.site_name)
    aggeragete_data["title"] = subject
    aggeragete_data["site_name"] = site.site_name
    aggeragete_data["duration"] = duration + "ly"
    aggeragete_data["date"] = now
    aggeragete_data["generator_stat"] = "NA" #TODO
    # TODO fix this
    aggeragete_data["url_to_dash"] = 'http://sesh.gle.solar/site/<site_name>'


    # TODO hack alert
    aggeragete_data["cost_savings"] = aggeragete_data["total_pv"] * cash_power_cost

    mail_sent = report(subject, aggeragete_data, recipients)
    return mail_sent

def report(subject,content,recipients):
    return send_mail(subject, recipients, content, email_template="reporting")


def generate_report(report):
    """
    Function to generate a report,
    The function receives a report model instance and
    it returns a dict containing the aggregated value of the 
    report attributes
    """ 
    report_data = {}
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
        table = apps.get_model(app_label="seshdash", model_name=attribute["table"])
        data = table.objects.filter(site=report.site
                                    date__range=[start, now]).aggregate(Sum(attribute["column"]))
        report_data.update(data)
                    
    return report_data                       
