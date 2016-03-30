from clickatell.rest import Rest
from django.conf import settings
from django.template.loader import get_template

clickatell = Rest(settings.CLICKATELL_KEY)

def send_sms(recipients, context, sms_template='alert'):
    # TODO Enhance the Sms template to contain useful inforamation
    sms_template = get_template('seshdash/sms/%s_sms.txt'%sms_template)
    sms = sms_template.render(context)
    print sms
    response = clickatell.sendMessage(recipients, sms)
    if not response[0]['errorCode']:
        print "Message Sent"
        return True
    else:
        return False
