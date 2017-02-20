from django.urls import reverse
from post_office import mail
from django.utils.translation import ugettext_lazy as _
from iran_list.settings import SITE_ADDRESS, EMAIL_HOST_USER


def send_reset_pass_mail(email, user_full_name, hash):
    email = mail.send(
        recipients=[email],
        sender=EMAIL_HOST_USER,
        subject=_(u'Iran List - Reset Password'),
        message=_(u'Rest Your Password'),
        html_message=_(u'hi dear {{ name }},<br> You can reset your password <a href="{{ link }}">here</a>!<br>'
                       'If you didn\'t ask to change your password, just ignore this email.'),
        context={'name': user_full_name,
                 'link': '%s%s' % (SITE_ADDRESS, reverse('reset_pass', args=(hash,)).replace('//', '/'))},
        priority='now',
    )
