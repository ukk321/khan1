import logging

from django.conf import settings
from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils import translation
from booking.utils import SESService
from email_templates.models import EmailTemplate

logger = logging.getLogger(__name__)
CHARSET = "UTF-8"


class HiringNotification:

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
            logger.exception(e)

    @staticmethod
    def render_and_dispatch_email(subject, recipients, email_template_name, context=None):

        if context is None:
            context = {}
        context.update({
            'applicant_name': context.get('applicant_name', ''),
            'applicant_email': context.get('applicant_email', ''),
            'applicant_message': context.get('applicant_message', ''),
            # Add more fields as needed
        })

        email_body = render_to_string(email_template_name + ".html", context)
        # Prepare list of "to" email addresses
        to_addresses = []
        to_addresses.extend(recipients) if type(recipients) == list else to_addresses.append(recipients)
        HiringNotification.dispatch_email(subject, email_body, to_addresses)

    @staticmethod
    def send_email_to_applicant(email, applicant_details):
        mail_content = EmailTemplate.objects.get(templates='Applicant_Mail')

        subject = f'{mail_content.subject}'
        message = mail_content.body

        # Extract name from applicant_details
        name = applicant_details.get('name', '')

        HiringNotification.render_and_dispatch_email(
            subject,
            email,
            "hiring_mail_user",
            {'applicant_name': name, 'message': message},

        )

    @staticmethod
    def send_application_mail_to_admin(email, applicant_details):
        mail_content = EmailTemplate.objects.get(templates='Employer_Mail')

        subject = f'{mail_content.subject}'
        message = mail_content.body
        name = applicant_details.get('name', '')
        HiringNotification.render_and_dispatch_email(
            subject,
            email,
            "hiring_mail_admin",
            context={'applicant_name': name, 'message': message},

        )

    @staticmethod
    def hiring_mail_user(email, applicant_details):
        mail_content = EmailTemplate.objects.get(templates='Applicant_Mail')

        subject = mail_content.subject
        body_template = Template(mail_content.body)
        if email and applicant_details:
            context = Context(applicant_details)
            email_body_content = body_template.render(context)

            # Render the admin_mail.html template with the email body content
            admin_mail_template = 'hiring_mail_user.html'
            admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})

            # Dispatch the email to the admin
            HiringNotification.dispatch_email(subject, admin_email_body_content, [email])
            msg = "Email has been sent successfully"

        else:
            msg = "Email or applicant details missing"
        return msg

    @staticmethod
    def send_mail_to_admin(email, applicant_details):
        mail_content = EmailTemplate.objects.get(templates='Employer_Mail')
        subject = mail_content.subject
        body_template = Template(mail_content.body)
        try:

            if email and applicant_details:
                context = Context(applicant_details)
                email_body_content = body_template.render(context)

                # Render the admin_mail.html template with the email body content
                admin_mail_template = 'hiring_mail_admin.html'
                admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})

                # Dispatch the email to the admin
                HiringNotification.dispatch_email(subject, admin_email_body_content, [email])
                msg = "Email has been sent successfully to admin"
            else:
                msg = "No applicants found"
        except Exception as e:
            msg = "No applicants found"
            logger.exception(f'Exception: {e}')
        return msg
