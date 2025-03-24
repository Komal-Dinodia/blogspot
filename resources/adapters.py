from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from allauth.account.utils import user_pk_to_url_str

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """Generate the frontend verification link for email confirmation."""
        return f"{settings.FRONTEND_URL}/verify-email/{emailconfirmation.key}"

    def send_mail(self, template_prefix, email, context):
        """
        Customize email sending for password reset while keeping other emails unchanged.
        """
        if template_prefix == "account/email/password_reset_key":
            user = context.get("user")
            if user:
                uid = user_pk_to_url_str(user)  # Get user's UID
                token = context["token"]
                context["password_reset_url"] = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        # Call the original method to send the email
        super().send_mail(template_prefix, email, context)

