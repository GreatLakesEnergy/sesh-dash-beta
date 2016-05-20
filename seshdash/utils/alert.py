from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert, Sesh_User, RMC_status, Slack_Channel
from seshdash.utils.send_mail import send_mail
from seshdash.utils.send_sms import send_sms
from seshdash.utils.model_tools import get_model_from_string, get_latest_instance
from django.utils import timezone
from guardian.shortcuts import get_users_with_perms, get_groups_with_perms
from django.conf import settings
from dateutil import parser

# Influx client
from seshdash.data.db import influx

from seshdash.utils.model_tools import get_model_first_reference
from seshdash.utils.time_utils import get_epoch_from_datetime
from seshdash.utils.send_slack import Slack

import logging

#Insantiating the logger
logger = logging.getLogger(__name__)

# Sends an email if the received data point fails to pass the defined rules for its site.

# New Alert Rules can be defined as below:

# Alert_Rule.objects.create(site = site, check_field="soc", value=30, operator="gt")
# Alert_Rule.objects.create(site = site, check_field="soc", value=35.5, operator="eq")
# Alert_Rule.objects.create(site = site, check_field="battery_voltage", value=25, operator="lt")

# Rules are based on sites. So you need to define a rule for each site if you want to check same configurations in several sites.
# A Sesh_Alert object is created for each 'alert triggered and an email is send if the rule has send_mail option true


def alert_generator():
    """ Generates alerts for a given site """
    mails = []
    sms_numbers = []
    rules = Alert_Rule.objects.all()

    for rule in rules:
        site = rule.site
        site_groups = get_groups_with_perms(site)

        # Get datapoint and real value
        data_point, real_value = get_alert_check_value(site, rule)

        if data_point is not None and real_value is not None:

            if check_alert(rule, real_value):

                alert_obj = alert_factory(site, rule, data_point)

                # if alert_obj is created
                if alert_obj is not None:
                    content = get_alert_content(site, rule, data_point, real_value, alert_obj)
                    mails, sms_numbers = get_recipients_for_site(site)


                    if rule.send_mail:
                         alert_obj.emailSent = alertEmail('Alert Email from seshdash',data_point,content,mails)

                    if rule.send_sms:
                         alert_obj.smsSent = alertSms(data_point,content,sms_numbers)

                    if rule.send_slack:
                         for site_group in site_groups:

                             # unpacking the neccessary data
                             sesh_organisation = site_group.sesh_organisation
                             channels = sesh_organisation.slack_channel.all().filter(is_alert_channel=True)


                             # instantiating the client
                             slack = Slack(sesh_organisation.slack_token)

                             for channel in channels:
                                 if settings.DEBUG == True:
                                     alert_obj.slackSent = True
                                 else:
                                     alert_obj.slackSent = slack.send_message_to_channel(channel.name, content['alert_str'])

                    alert_obj.save()





def alertEmail(subject, data_point,content,recipients):
    return send_mail(subject,recipients,content)



def alertSms(data_point,content,recipients):
    return send_sms(recipients, content)



def get_alert_check_value(site, rule):
    """ Returns the value to check for alert from latest data point """

    if is_mysql_rule(rule):
        model, field_name = rule.check_field.split('#')
        latest_data_point = get_latest_data_point_mysql(site, rule)

        if latest_data_point is not None:
            data_point_value = getattr(latest_data_point, field_name)
        else:
            data_point_value = None
            logger.error("No data points for %s", model)

        return latest_data_point, data_point_value

    elif is_influx_rule(rule):
        # Getting the datapoint from influx
        latest_data_point = get_latest_point_influx(site, rule)

        if latest_data_point is not None:
            data_point_value = latest_data_point['value']
            return latest_data_point, data_point_value
        else:
            return None, None

    else:
        return None, None

def get_latest_point_influx(site, rule):
    latest_data_point = influx.get_latest_point_site(site, rule.check_field, settings.INFLUX_DB)
    return latest_data_point

def get_latest_point_value_influx(site, rule):
    latest_data_point_value = get_latest_point_influx(site,rule)
    return latest_data_point_value['value']

def is_influx_rule(rule):
    """
       A function that detects if the alert rule defined uses influx,
       Influx rules should not contain a '#' because split returns
    """
    if len(rule.check_field.split('#')) == 1:
        return True
    else:
        return False


def is_mysql_rule(rule):
    """ A function that detects if the alert rule defined, uses mysql """

    if len(rule.check_field.split('#')) == 2:
        return True
    else:
        return False




def check_alert(rule, data_point_value):
    """ Checks the alert and returns boolean value true if there is alert and false otherwise """


    ops = {'lt': lambda x,y: x<y,
           'gt': lambda x,y: x>y,
           'eq' : lambda x,y: x==y,
    }

    """ If there is an alert """
    if ops[rule.operator](data_point_value,rule.value):
        return True

    else:
        return False



def get_alert_content(site, rule, data_point, value, alert):
    """ Returns a dictionary containing information about the alert """

    content = {}

    content_str = "site:%s\nrule:%s '%s' %s --> found %s " %(site.site_name,rule.check_field,rule.operator,rule.value, value)

    # Get ready content for email
    content['site'] = site.site_name
    content['alert_str'] = content_str
    content['alert'] = alert

    # Handling content for influx
    if is_influx_rule(rule):
        content['time'] = data_point['time']
    else:
        content['time'] = data_point.time
    content['data_point'] = data_point

    return content


def get_recipients_for_site(site):
    """ Returns mails and sms of users with allowance to recieve messages for site """
    users = get_users_with_perms(site)
    mails = []
    sms_numbers = []

    # TODO to be removed
    for user in users:


        if hasattr(user, 'seshuser'):
            mails.append(user.email)

            if user.seshuser.phone_number and user.seshuser.on_call:
                sms_numbers.append(user.seshuser.phone_number)


                logger.debug("emailing %s" % mails)

    return mails, sms_numbers



def alert_factory(site, rule, data_point):
    """ Creating an alert object """

    # Getting the last alert for rule
    point = rule.alert_point.last()

    alert_obj = None

    # If the last alert exists does not exist
    if point is None:
        alert_obj = create_alert_instance(site, rule, data_point)

    # if there is a last alert check if it is silenced
    else:
        # if the last alert is silenced create an alert
        if point.isSilence is True:
            alert_obj = create_alert_instance(site, rule, data_point)

    return alert_obj


def create_alert_instance(site, rule, data_point):
    if is_mysql_rule(rule):
        alert_obj = Sesh_Alert.objects.create(
                    site = site,
                    alert=rule,
                    date=timezone.now(),
                    isSilence=False,
                    emailSent=False,
                    slackSent=False,
                    smsSent=False,
                    point_model=type(data_point).__name__,
                    point_id= str(data_point.id ))
        alert_obj.save()

            # Set data point to point to alert
        data_point.target_alert = alert_obj
        data_point.save()

    elif is_influx_rule(rule):
        alert_obj = Sesh_Alert.objects.create(
                    site = site,
                    alert = rule,
                    date = timezone.now(),
                    isSilence=False,
                    emailSent=False,
                    slackSent=False,
                    smsSent=False,
                    point_model='influx',
                    point_id = get_epoch_from_datetime(parser.parse(data_point['time'])))
    alert_obj.save()
    return alert_obj




def get_unsilenced_alerts():
    """ Return the unsilenced alerts of a site if any, otherwiser returns false """
    unsilenced_alerts = Sesh_Alert.objects.filter(isSilence=False)

    if unsilenced_alerts:
        return unsilenced_alerts
    else:
        return []


def get_latest_instance_site(site, model):
    """ Returns latest instance for models with site """
    latest_instance_site = model.objects.filter(site=site).order_by('-id')


    if latest_instance_site:
        return latest_instance_site[0]
    else:
        return None


def get_latest_data_point_mysql(site, rule):
    """ Returns the latest point in the model specified in the rule checkfield"""
    model, field_name = rule.check_field.strip().split('#') # Get model and field names

    # Getting the model name and the latest value of the model field
    model = get_model_from_string(model)  # returns a model class ex 'BoM_Data_Point'
    latest_data_point = get_latest_instance_site(site, model)

    return latest_data_point

def get_latest_data_point_value_mysql(site, rule):
    """ Returns the value to check for the value of the latest point for model in the rule checkfield """
    model, field_name = rule.check_field.strip().split('#')

    # Getting the model name and the latest value of the model field
    model = get_model_from_string(model)
    latest_data_point = get_latest_instance_site(site, model)
    latest_data_point_value = getattr(latest_data_point, field_name)

    return latest_data_point_value


def get_alert_point(alert):
    """ Returns a point that triggers the alert """
    model_name = alert.point_model
    rule = alert.alert
    check_field = alert.alert.check_field

    if is_influx_rule(rule):
        point = influx.get_point(check_field, alert.point_id)

    else:
        point = get_model_first_reference(model_name, alert)

    return point

def get_alert_point_value(alert, point=None):
    """ Returns the value that triggers the alert """
    rule = alert.alert
    if not point:
        point = get_alert_point(alert)

    # Handle if alert has no point, (no puns intended)
    if not point:
        return None

    # Get the alert data
    if is_mysql_rule(rule):
        model, field_name = rule.check_field.strip().split('#')
        value = getattr(point, field_name)

    elif is_influx_rule(rule):
        value = point['value']


    return value




def alert_status_check():
    """ Checks if the alert is still valid and silences it if it is invalid """
    unsilenced_alerts = get_unsilenced_alerts()
    logger.debug("Running alert status check")
    if unsilenced_alerts:
        for alert in unsilenced_alerts:
            site = alert.site
            rule = alert.alert

            if is_mysql_rule(rule):
                latest_data_point_value = get_latest_data_point_value_mysql(site, rule)
            elif is_influx_rule(rule):
                latest_data_point_value = get_latest_point_value_influx(site, rule)
            else:
                logger.error('Invaliid rule')
                return None


            if check_alert(rule, latest_data_point_value):
                logger.debug("Alert is still valid")
            else:
                # Silencing the alert and generating email content
                alert.isSilence = True
                alert.save()
                data_point = get_alert_point(alert)
                data_point_value = get_alert_point_value(alert, data_point)

                # Handle no data point getting returned
                if not data_point_value:
                    logger.warning("Now DP found for alert skipping ")
                    return None

                content = get_alert_content(site, rule, data_point, data_point_value, alert)

                mails, sms_numbers = get_recipients_for_site(site)

                # Reporting
                if rule.send_mail:
                    alertEmail('Alert auto silenced', data_point, content, mails)

                if rule.send_sms:
                    alertSms(data_point,content,sms_numbers)
