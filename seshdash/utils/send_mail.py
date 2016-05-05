from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from sesh.settings import FROM_EMAIL

import traceback
import logging

# example: send_mail("Hello World", [me@gmail.com,you@gmail.com],"Here is your email")
# Sends and email to me@gmail.com and you@gmail.com addresses an email
# with subject "Hello World" and body including "Here is your email"
def send_mail(subject,list_of_recipients,content,email_template='alert'):
    try:
        print "Message to be sent with subject %s and recipients %s" % (subject, list_of_recipients)
        if not  list_of_recipients:
            return False
        plaintext = get_template('seshdash/mail/%s_mail.txt'%email_template)
        htmly    = get_template('seshdash/mail/%s_mail.html'%email_template)
        d = { 'username' : "User",
              'content'  : content,
                      }
        text_content = plaintext.render(d)
        html_content = htmly.render(d)

        logging.debug(html_content)
        msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL, list_of_recipients)
        msg.attach_alternative(html_content, "text/html")
        result = msg.send()
        print "MEssage sent"
        if not result:
            raise Exception("Error sending email result:%s"%result)
        return True

    except Exception,e:
        traceback.print_exc()
        import rollbar
        rollbar.report_message("Error sending email with content %s "%content)
        rollbar.report_exc_info()
        return False
