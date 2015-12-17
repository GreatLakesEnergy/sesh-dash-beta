from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from sesh.settings import FROM_EMAIL

import traceback

# example: send_mail("Hello World", [me@gmail.com,you@gmail.com],"Here is your email")
# Sends and email to me@gmail.com and you@gmail.com addresses an email
# with subject "Hello World" and body including "Here is your email"
def send_mail(subject,list_of_recipients,content):
    try:
        plaintext = get_template('mail/site_mail.txt')
        htmly     = get_template('mail/site_mail.html')
        d = Context({ 'username' : "User",
                      'content'  : content,
                      })
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL, list_of_recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except:
        traceback.print_exc()
        return False
