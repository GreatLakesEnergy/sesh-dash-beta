from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from sesh.settings import FROM_EMAIL

import traceback
import logging

# Instantiating the logger
logger = logging.getLogger(__name__)

# example: send_mail("Hello World", [me@gmail.com,you@gmail.com],"Here is your email")
# Sends and email to me@gmail.com and you@gmail.com addresses an email
# with subject "Hello World" and body including "Here is your email"
def send_mail(subject,list_of_recipients,content,email_template='alert'):
    try:
        if not  list_of_recipients:
            return False
        plaintext = get_template('seshdash/mail/%s_mail.txt'%email_template)
        htmly    = get_template('seshdash/mail/%s_mail.html'%email_template)
        d = { 'username' : "User",
              'content'  : content,
                      }
        text_content = plaintext.render(d)
        html_content = htmly.render(d)

        msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL, list_of_recipients)
        msg.attach_alternative(html_content, "text/html")
        result = msg.send()
        if not result:
            raise Exception("Error sending email result:%s"%result)
        return True

    except Exception,e:
        traceback.print_exc()
        import rollbar
        rollbar.report_message("Error sending email with content %s "%content)
        rollbar.report_exc_info()
        return False
