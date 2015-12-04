from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import traceback

def send_mail(subject,to_email):
    try:
        plaintext = get_template('mail/site_mail.txt')
        htmly     = get_template('mail/site_mail.html')
        d = Context({ 'username' : "User2"
                      })
        from_email = "seshdash@gmail.com"
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except:
        traceback.print_exc()
