import logging

from django.conf import settings
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils import translation

from booking.utils import SESService
from email_templates.models import EmailTemplate

logger = logging.getLogger(__name__)
CHARSET = "UTF-8"


class Notification:

    def language_based_render_to_string(
            template_name, language=settings.LANGUAGE_CODE
    ):
        """
        This function renders template to string based on language
        Activates preferred language for string translation
        Reactivates request language for response message translations (if any)
        """
        _lang = translation.get_language()
        translation.activate(language)
        body = render_to_string(template_name)
        translation.activate(_lang)
        return body

    @classmethod
    def render_email_body(cls, email_template_name, language_code):
        email_body = cls.language_based_render_to_string(email_template_name)
        if language_code not in settings.LANGUAGE_CODE:  # e.g. "en" not in "en-us"
            translated_email_body = cls.language_based_render_to_string(
                email_template_name, language_code
            )
            # todo: detect language code - might have to make use of some library
            # makeshift: comparing both bodies
            if translated_email_body != email_body:
                email_body = email_body + "<br><br>" + translated_email_body
            else:
                logger.warning(
                    f"User's preferred language {language_code} is supported but not fully translated!"
                )
        return email_body

    @classmethod
    def dispatch_email(cls, subject, email_body, recipients):
        try:
            SESService.dispatch_email(subject, email_body, recipients)
        except Exception as e:
            logger.info(e)

    @staticmethod
    def render_and_dispatch_email(subject, recipients, email_template_name, context=None,
                                  reply_message=None):

        if context is None:
            context = {}

        # Add reply_message to the context
        context['reply_message'] = reply_message

        # Render the template with updated context data
        email_body = render_to_string(email_template_name + ".html", context)

        # Prepare list of "to" email addresses
        to_addresses = []
        to_addresses.extend(recipients) if type(recipients) == list else to_addresses.append(recipients)

        # Dispatch the email
        Notification.dispatch_email(subject, email_body, to_addresses)

    @staticmethod
    def send_query_email(email, name, message):

        mail_content = EmailTemplate.objects.get(templates='Contact_Us_Client')

        subject = f'{mail_content.subject}'
        body_template = Template(mail_content.body)

        context = Context({'name': name, 'message': message})
        email_body_content = body_template.render(context)

        # Render the admin_mail.html template with the email body content
        admin_mail_template = 'contact_us_mail.html'
        admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})

        # Dispatch the email to the admin
        Notification.dispatch_email(subject, admin_email_body_content, [email])

        msg = "Email has been sent successfully to admin"
        return msg

    @staticmethod
    def send_query_email_to_admin(email, name):
        mail_content = EmailTemplate.objects.get(templates='Contact_Us_Admin')

        subject = f'{mail_content.subject}'
        message = mail_content.body

        Notification.render_and_dispatch_email(
            subject,
            email,
            "admin_mail",
            {'name': name, 'message': message},

        )

    @staticmethod
    def send_query_received_mail(email, language_code, name, message):
        if email:
            Notification.send_query_email(email, name, message)
            msg = "Email has been sent successfully"

            return msg

    @staticmethod
    def send_mail_to_admin(email, name, message, inquiry_id):
        mail_content = EmailTemplate.objects.get(templates='Contact_US_Admin')

        subject = mail_content.subject
        body_template = Template(mail_content.body)

        if email:
            # Construct the link to the reply page using the inquiry_id
            admin_reply_link = settings.EMAIL_REPLY_URL.format(inquiry_id)

            # Render the email body template
            context = Context({'name': name, 'message': message, 'admin_reply_link': admin_reply_link})
            email_body_content = body_template.render(context)

            # Render the admin_mail.html template with the email body content
            admin_mail_template = 'admin_mail.html'
            admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})

            # Dispatch the email to the admin
            Notification.dispatch_email(subject, admin_email_body_content, [email])

            msg = "Email has been sent successfully to admin"
            return msg

    @staticmethod
    def send_email_to_user(email, reply_message, name):
        mail_content = EmailTemplate.objects.get(templates='Reply_User')
        subject = f'{mail_content.subject}'
        body_template = Template(mail_content.body)

        context = Context({'name': name, 'message': reply_message})

        email_body_content = body_template.render(context)

        admin_mail_template = 'reply_template.html'

        # Render the email body template with reply_message and name
        admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})

        Notification.dispatch_email(subject, admin_email_body_content, email)
