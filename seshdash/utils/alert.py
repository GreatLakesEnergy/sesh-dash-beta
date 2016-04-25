from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert, Sesh_User, RMC_status
from seshdash.utils.send_mail import send_mail
from seshdash.utils.send_sms import send_sms
from seshdash.utils.model_tools import get_model_from_string
from django.utils import timezone
from guardian.shortcuts import get_users_with_perms
import logging

# Sends an email if the received data point fails to pass the defined rules for its site.

# New Alert Rules can be defined as below:

# Alert_Rule.objects.create(site = site, check_field="soc", value=30, operator="gt")
# Alert_Rule.objects.create(site = site, check_field="soc", value=35.5, operator="eq")
# Alert_Rule.objects.create(site = site, check_field="battery_voltage", value=25, operator="lt")

# Rules are based on sites. So you need to define a rule for each site if you want to check same configurations in several sites.
# A Sesh_Alert object is created for each 'alert triggered and an email is send if the rule has send_mail option true
def alert_check(site):
    ops = {'lt': lambda x,y: x<y,
           'gt': lambda x,y: x>y,
           'eq' : lambda x,y: x==y,
    }
    email_recipients = []
    sms_recipients = []
    content = {}
    rules = Alert_Rule.objects.filter(site = site)

    for rule in rules:
         
        """ If the rule contains a model and a field, valid for  using model#checkfield """
        if '#' in rule.check_field: 
            model, field_name = rule.check_field.split('#')
             
            # Getting the model name and the latest value of the model field
            model = get_model_from_string(model)
            data_point = model.objects.all().order_by('-id')[0]
            real_value = getattr(data_point, field_name)


        """ If there is an alert """
        if ops[rule.operator](real_value,rule.value):
            content_str = "site:%s\nrule:%s '%s' %s --> found %s " %(site.site_name,rule.check_field,rule.operator,rule.value,real_value)

            # Get ready content for email
            content['site'] = site.site_name
            content['alert'] = content_str
            content['time'] = data_point.time
            content['data_point'] = data_point

            # TODO rule object should have the list of related persons to send alert mail
            users = get_users_with_perms(site)

            # TODO to be removed
            for user in users:
                email_recipients.append(user.email)
                if user.seshuser.phone_number and user.seshuser.on_call:
                    sms_recipients.append(user.seshuser.phone_number)


            logging.debug("emailing %s" %email_recipients)
            #print "emailing %s"%recipients
            # recipients = ["seshdash@gmail.com",]
            
            """ Creating an alert object """
            alert_obj = Sesh_Alert.objects.create(
                    site = site,
                    alert=rule,
                    date=timezone.now(),
                    isSilence=False,
                    emailSent=False,
                    slackSent=False,
                    smsSent=False,
                    point_model=type(data_point).__name__ )
            alert_obj.save()
            
            
            # Set data point to point to alert
            data_point.target_alert = alert_obj
            data_point.save()
            alerts = Sesh_Alert.objects.all()


            if rule.send_mail:
                mail_sent = alertEmail(data_point,content,email_recipients)
                alert_obj.emailSent = mail_sent
            
            if rule.send_sms:
                sms_response = alertSms(data_point,content,sms_recipients)
                alert_obj.smsSent = sms_response
            
            alert_obj.save()

def alertEmail(data_point,content,recipients):
    return send_mail("Alert email from seshdash",recipients,content)

def alertSms(data_point,content,recipients):
    return send_sms(recipients, content)

def unsilenced_alerts(site):
    """ Return the unsilenced alerts of a site if any, otherwiser returns false """
    unsilenced_alerts = Sesh_Alert.objects.filter(site=site, isSilence=True)

    if unsilenced_alerts:
        return unsilenced_alerts
    else:
        return False
