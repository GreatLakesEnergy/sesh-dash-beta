from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert
from seshdash.utils.send_mail import send_mail
from django.utils import timezone
from guardian.shortcuts import get_users_with_perms
import logging

# Sends an email if the received data point fails to pass the defined rules for its site.

# New Alert Rules can be defined as below:

# Alert_Rule.objects.create(site = site, check_field="soc", value=30, operator="gt")
# Alert_Rule.objects.create(site = site, check_field="soc", value=35.5, operator="eq")
# Alert_Rule.objects.create(site = site, check_field="battery_voltage", value=25, operator="lt")

# Rules are based on sites. So you need to define a rule for each site if you want to check same configurations in several sites.
# A Sesh_Alert object is created for each alert triggered and an email is send if the rule has send_mail option true
def alert_check(data_point):
    ops = {'lt': lambda x,y: x<y,
           'gt': lambda x,y: x>y,
           'eq' : lambda x,y: x==y,
    }
    recipients = []
    rules = Alert_Rule.objects.filter(site = data_point.site)
    for rule in rules:
        real_value = getattr(data_point,rule.check_field)
        if ops[rule.operator](real_value,rule.value):
            content = "site:%s\nrule:%s '%s' %s --> found %s " %(data_point.site.site_name,rule.check_field,rule.operator,rule.value,real_value)
            # TODO rule object should have the list of related persons to send alert mail
            users = get_users_with_perms(data_point.site)
            for user in users:
                recipients.append(user.email)
            logging.debug("emailing %s" %recipients)
            print "emailing %s"%recipients
            # recipients = ["seshdash@gmail.com",]
            alert_obj = Sesh_Alert.objects.create(site = data_point.site, alert=rule, date=timezone.now(),
                                                  isSilence=True,alertSent=rule.send_mail, point=data_point)
            if rule.send_mail:
                mail_sent = alert(data_point,content,recipients)
                alert_obj.alertSent = mail_sent
                print("Sent mail for %s" %content)
            alert_obj.save()

def alert(data_point,content,recipients):
    return send_mail("Alert email from seshdash",recipients,content)
