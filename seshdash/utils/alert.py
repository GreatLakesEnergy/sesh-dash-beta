from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert, Sesh_User, RMC_status
from seshdash.utils.send_mail import send_mail
from seshdash.utils.send_sms import send_sms
from seshdash.utils.model_tools import get_model_from_string, get_latest_instance
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


def alert_generator(site):
    """ Generates alerts for a given site """ 
    mails = []
    sms_numbers = []
    rules = Alert_Rule.objects.filter(site = site)

    for rule in rules:
        # Get datapoint and value
        data_point, real_value = get_alert_check_value(site, rule)

        if data_point is not None and real_value is not None:

            if check_alert(rule, real_value):
                content = get_alert_content(site, rule, data_point, real_value)
                mails, sms_numbers = get_recipients_for_site(site)
          
                alert_obj = alert_factory(site, rule, data_point)

                if rule.send_mail:
                     alert_obj.emailSent = alertEmail(data_point,content,mails)
            
                if rule.send_sms:
                     alert_obj.smsSent = alertSms(data_point,content,sms_numbers)
            
                alert_obj.save()




def alertEmail(data_point,content,recipients):
    return send_mail("Alert email from seshdash",recipients,content)



def alertSms(data_point,content,recipients):
    return send_sms(recipients, content)



def get_alert_check_value(site, rule):
    """ Returns the value to check for alert from latest data point """
      
    # if rule is valid
    if '#' in rule.check_field:
        model, field_name = rule.check_field.split('#')
        latest_data_point = get_latest_data_point_for_rule(site, rule)
        
        if latest_data_point is not None:
            data_point_value = getattr(latest_data_point, field_name)
        else:
            data_point_value = None
            logging.error("No data points for %s", model)
        
        return latest_data_point, data_point_value

    else:
        logging.error('Invalid alert rule')
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



def get_alert_content(site, rule, data_point, value):
    """ Returns a dictionary containing information about the alert """

    content = {}

    content_str = "site:%s\nrule:%s '%s' %s --> found %s " %(site.site_name,rule.check_field,rule.operator,rule.value, value)

    # Get ready content for email
    content['site'] = site.site_name
    content['alert'] = content_str
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
                print user
                print "User seshuser phonenumber: ",
                print user.seshuser.phone_number
                sms_numbers.append(user.seshuser.phone_number)


                logging.debug("emailing %s" % mails)
                #print "emailing %s"%recipients
            
    return mails, sms_numbers
    

def alert_factory(site, rule, data_point):
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
   
    return alert_obj

   

def unsilenced_alerts(site):
    """ Return the unsilenced alerts of a site if any, otherwiser returns false """
    unsilenced_alerts = Sesh_Alert.objects.filter(site=site, isSilence=False)

    if unsilenced_alerts:
        return unsilenced_alerts
    else:
        return False


def get_latest_instance_site(site, model):
    """ Returns latest instance for models with site """
    latest_instance_site = model.objects.filter(site=site).order_by('-id')
    latest_instance_site = model.objects.filter(site=site).order_by('-id')

    
    if latest_instance_site:
        return latest_instance_site[0]
    else:
        return None


def get_latest_data_point_for_rule(site, rule):

    model, field_name = rule.check_field.split('#') # Get model and field names

    # Getting the model name and the latest value of the model field
    model = get_model_from_string(model)  # returns a model class ex 'BoM_Data_Point'
    latest_data_point = get_latest_instance_site(site, model)

    return latest_data_point

def get_latest_data_point_value_for_rule(site, rule):
    
    model, field_name = rule.check_field.split('#')

    # Getting the model name and the latest value of the model field
    model = get_model_from_string(model)
    latest_data_point = get_latest_instance_site(site, model)
    latest_data_point_value = getattr(latest_data_point, field_name)
   
    return latest_data_point_value



def alert_status_check():
    """ Checks if the alert is still valid and silences it if it is invalid """
    unsilenced_alerts = Sesh_Alert.objects.filter(isSilence=False)
    
    for alert in unsilenced_alerts:
        site = alert.site
        rule = alert.alert
        latest_data_point_value = get_latest_data_point_value_for_rule(site, rule) 

        if check_alert(rule, latest_data_point_value):
            print "The alert is still valid"
        else:
            alert.isSilence = True
            alert.save()
