import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import Template, Context
from django.utils import translation
from django.conf import settings
from email_templates.models import EmailTemplate
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:

    def dispatch_email(subject, email_body, recipients):        
        if not recipients:
            logger.error("No recipients provided for email.")
            return
        
        if not subject or not email_body:
            logger.error("Subject or email body missing.")
            return
        today=datetime.now().strftime('%d-%m-%Y')
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                from_email=settings.EMAIL_SENDER,
                to=recipients,
            )
            msg.attach_alternative(email_body, "text/html")
            msg.send()
            logger.info(f"Email sent successfully to {recipients} on {today}")
        except Exception as e:
            module_name=__name__
            logger.exception(f"Failed to send email: {e} in {module_name}:{e}")

    def render_email_template(template_name, context, language_code=settings.LANGUAGE_CODE):
        logger.info(f"Rendering email template: {template_name} with context: {context}")
        _lang = translation.get_language()
        translation.activate(language_code)
        email_body = render_to_string(template_name, context)
        translation.activate(_lang)
        return email_body

    @staticmethod
    def send_email_with_template_key(template_key, recipients, context):
        try:
            mail_content = EmailTemplate.objects.get(templates=template_key)
            
            template = Template(mail_content.body)
            rendered_body = template.render(Context(context))
            
            final_email_body = EmailService.render_email_template(
                f'{template_key}.html',
                {'message': rendered_body},
            )

            EmailService.dispatch_email(mail_content.subject, final_email_body, recipients)

        except EmailTemplate.DoesNotExist:
            logger.error(f"Email template with key '{template_key}' does not exist.")
        except Exception as e:
            logger.error(f"Failed to send email with template '{template_key}': {e}")
