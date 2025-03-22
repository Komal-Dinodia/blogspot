from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from allauth.account.utils import user_pk_to_url_str


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """Generate the frontend verification link instead of the backend."""
        frontend_url = f"{settings.FRONTEND_URL}/verify-email/{emailconfirmation.key}"
        return frontend_url


class CustomPasswordResetAdapter(DefaultAccountAdapter):
    def send_password_reset_mail(self, request, email, context):
        """Modify the password reset link to use the frontend URL."""
        uid = user_pk_to_url_str(context["user"])
        token = context["token"]
        frontend_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
        context["password_reset_url"] = frontend_url

        # Call the original method to send the email
        super().send_mail("account/email/password_reset_key", email, context)
