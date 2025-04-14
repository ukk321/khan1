import logging
import smtplib
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils import translation
from email_templates.models import EmailTemplate

logger = logging.getLogger(__name__)
CHARSET = "UTF-8"


class SESService:
    # @staticmethod
    # def get_client():
    #     return client(
    #         "ses",
    #         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #         region_name=settings.AWS_S3_REGION_NAME,
    #     )

    @staticmethod
    def dispatch_email(subject, email_body, recipients):
        logger.info(f"Sending email to {recipients}")
        # ses_client = SESService.get_client()
        if settings.EMAIL_ENABLED:
            if settings.EMAIL_SENDER is None:
                logger.error("SES email sender is not configured. Please set 'EMAIL_SENDER' in settings.")
                return  # Exit early if SES email sender is not configured

            try:

                # Create the email object
                msg = EmailMultiAlternatives(
                    subject=subject,
                    from_email=settings.EMAIL_SENDER,
                    to=recipients,
                )

                # Attach the HTML email body
                msg.attach_alternative(email_body, "text/html")

                # Send the email
                msg.send()

                # Return a success message
                logger.info("Email sent successfully")

            except smtplib.SMTPException as e:
                # Catch SMTP errors and handle them
                e = str(e)
                logger.info(f'SMTP Exception --------- {e}')

            except Exception as e:
                # Catch other general exceptions
                e = str(e)
                logger.info(f'Exception --------- {e}')

        else:
            logger.warning("Email not enabled in settings")


class BookingNotification:

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
                                  ):

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
        BookingNotification.dispatch_email(subject, email_body, to_addresses)

    @staticmethod
    def send_email_to_applicant(email, booking_details):
        mail_content = EmailTemplate.objects.get(templates='Booking_Client')

        subject = f'{mail_content.subject}'
        message = mail_content.body

        name = booking_details.get('name', '')

        BookingNotification.render_and_dispatch_email(
            subject,
            email,
            "booking_client",
            {'applicant_name': name, 'message': message},
        )

    @staticmethod
    def send_application_mail_to_admin(email, applicant_details):
        mail_content = EmailTemplate.objects.get(templates='Booking_Admin')

        subject = f'{mail_content.subject}'
        message = mail_content.body
        name = applicant_details.get('name', '')

        BookingNotification.render_and_dispatch_email(
            subject,
            email,
            "booking_admin",
            {'applicant_name': name, 'message': message},
        )

    @staticmethod
    def feedback_mail_user(email, booking_details):
        mail_content = EmailTemplate.objects.get(templates='Booking_Client')

        subject = f'{mail_content.subject}'
        body_template = Template(mail_content.body)
        if email and booking_details:
            context = Context(booking_details)
            email_body_content = body_template.render(context)

            # Render the admin_mail.html template with the email body content
            admin_mail_template = 'booking_client.html'
            admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})

            # Dispatch the email to the admin
            BookingNotification.dispatch_email(subject, admin_email_body_content, [email])

    @staticmethod
    def send_mail_to_admin(email, applicant_details):
        mail_content = EmailTemplate.objects.get(templates='Booking_Admin')
        subject = mail_content.subject
        body_template = Template(mail_content.body)
        try:
            if email and applicant_details:
                context = Context(applicant_details)
                email_body_content = body_template.render(context)
                admin_mail_template = 'booking_admin.html'
                admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})
                # Dispatch the email to the admin
                BookingNotification.dispatch_email(subject, admin_email_body_content, [email])

                msg = "Email has been sent successfully to admin"
            else:
                msg = "No applicants found"
        except Exception as e:
            msg = "No applicants found"
            logger.exception(f'Exception: {e}')
        return msg

    @staticmethod
    def send_confirmation_mail_to_user(email,  feedback_details):
        mail_content = EmailTemplate.objects.get(templates='Booking_Confirmation')
        subject = mail_content.subject
        body_template = Template(mail_content.body)

        # Render and dispatch the email using the existing method
        if email and feedback_details:
            context = Context(feedback_details)
            email_body_content = body_template.render(context)

            # Render the admin_mail.html template with the email body content
            admin_mail_template = 'booking_confirmation.html'
            admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})

            # Dispatch the email to the admin
            BookingNotification.dispatch_email(subject, admin_email_body_content, [email])

        # Log or print success message for feedback approval mail
        logger.info(f"Approval email sent to user {email}")

        # Return a success message
        return f"Approval email sent to user: {email}"

    @staticmethod
    def send_otp_mail_to_user(email, feedback_details):
        mail_content = EmailTemplate.objects.get(templates='Booking_OTP')
        subject = mail_content.subject
        body_template = Template(mail_content.body)

        # Render and dispatch the email using the existing method
        if email and feedback_details:
            context = Context(feedback_details)
            email_body_content = body_template.render(context)

            # Render the admin_mail.html template with the email body content
            admin_mail_template = 'booking_otp.html'
            admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})

            # Dispatch the email to the admin
            BookingNotification.dispatch_email(subject, admin_email_body_content, [email])

        # Log or print success message for feedback approval mail
        logger.info(f"OTP sent to user {email}")

        # Return a success message
        return f"OTP sent to user: {email}"

    @staticmethod
    def send_cancellation_mail_to_user(email, feedback_details):
        mail_content = EmailTemplate.objects.get(templates='Booking_Cancellation')
        subject = mail_content.subject
        body_template = Template(mail_content.body)

        # Render and dispatch the email using the existing method
        if email and feedback_details:
            context = Context(feedback_details)
            email_body_content = body_template.render(context)

            # Render the admin_mail.html template with the email body content
            admin_mail_template = 'booking_cancellation.html'
            admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_content})

            # Dispatch the email to the admin
            BookingNotification.dispatch_email(subject, admin_email_body_content, [email])

        logger.info(f"Cancellation Mail sent to user {email}")

        # Return a success message
        return f"Cancellation Mail sent to user: {email}"

    @staticmethod
    def send_time_allocation_mail_to_user(email, feedback_details):
        mail_content = EmailTemplate.objects.get(templates='Booking_Time_Allocation')
        subject = mail_content.subject
        body_template = Template(mail_content.body)

        if email and feedback_details:
            context = Context(feedback_details)
            email_body_context = body_template.render(context)

            admin_mail_template = 'booking_time_allocation.html'
            admin_email_body_content = render_to_string(admin_mail_template, {'message': email_body_context})

            BookingNotification.dispatch_email(subject, admin_email_body_content, [email])

        logger.info(f'Time Allocation Mail sent to user {email}')

        return f'Time Allocation Mail sent to user {email}'
