from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert,Daily_Data_Point
from seshdash.utils.send_mail import send_mail

from django.utils import timezone
from django.db.models import Avg,Sum

from guardian.shortcuts import get_users_with_perms
from datetime import datetime
from datetime import timedelta
import logging

# Sends an email of reporting data on past duration

def prepare_report(site, duration="week"):
    """
    Get aggregate data points for the given duration
    duration options are "1w","1m"
    TODO make this date parsing part of time utils class

    """
    recipients = []
    cash_power_cost = 200

    now = datetime.now()
    #TODO  This is terrible make decent date parser!
    if duration == "week":
        date_range = now - timedelta(days=7)
    else:
        duration = "month"
        date_range = now - timedelta(month=1)


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
    # Get Users for site
    users = get_users_with_perms(site)
    for user in users:
        recipients.append(user.email)
    logging.debug("emailing %s" %recipients)

    # Add in meta
    subject = "%sly energy usage for %s"%(duration,site.site_name)
    aggeragete_data["title"] = subject
    aggeragete_data["site_name"] = site.site_name
    aggeragete_data["duration"] = duration
    aggeragete_data["generator_stat"] = "NA" #TODO
    # TODO fix this
    aggeragete_data["url_to_dash"] = 'http://sesh-dev1.cloudapp.net:3030/site/<site_name>'


    # TODO hack alert
    aggeragete_data["cost_savings"] = aggeragete_data["total_pv"] * cash_power_cost

    mail_sent = report(subject, aggeragete_data, recipients)
    return mail_sent

def report(subject,content,recipients):
    return send_mail(subject, recipients, content, email_template="reporting")



