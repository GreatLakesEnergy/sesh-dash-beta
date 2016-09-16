from clickatell.rest import Rest
from django.conf import settings
from django.template.loader import get_template
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_sms(recipients, context, sms_template='alert'):
    response = False

    if not recipients:
        logger.debug("No recipients for alert")
        return False

    if settings.CLICKATELL_KEY == 'your_clickatell_key' or settings.DEBUG:
        clicksms = False
    else:
        clicksms = Rest(settings.CLICKATELL_KEY)

    # TODO Enhance the Sms template to contain useful inforamation
    sms_template = get_template('seshdash/sms/%s_sms.txt'%sms_template)
    sms = sms_template.render(context)
    
    if clicksms:
        if not settings.DEBUG:
            response = clicksms.sendMessage(recipients, sms)
            print "The clickatell response is: %s" % response
            response = not response[0]['errorCode']
    
    return response
