from seshdash.models import Sesh_Site,Site_Weather_Data,BoM_Data_Point, Alert_Rule, Sesh_Alert
from seshdash.utils.send_mail import send_mail
from datetime import datetime

def alert_check(data_point):
    ops = {'lt': lambda x,y: x<y,
           'gt': lambda x,y: x>y,
           'eq' : lambda x,y: x==y,
    }
    rules = Alert_Rule.objects.filter(site = data_point.site)
    for rule in rules:
        real_value = getattr(data_point,rule.check_field)
        if ops[rule.operator](real_value,rule.value):
            content = "site:%s\nrule:%s '%s' %s --> found %s " %(data_point.site.site_name,rule.check_field,rule.operator,rule.value,real_value)
            alert(data_point,content)
            alert_obj = Sesh_Alert.objects.create(site = data_point.site, alert=rule, date=datetime.now(),isSilence=True,alertSent=rule.send_mail)
            print("Sent mail for %s" %content)

def alert(data_point,content):
    send_mail("Alert email from seshdash","seshdash@gmail.com",content)
