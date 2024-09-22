import random
import string

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )

class ResetPassword(PasswordResetTokenGenerator):
    def _make_hash_value(self, user):
        return (
            six.text_type(user.pk)
        )

# Instantiate the token generators
account_activation_token = TokenGenerator()
reset_password = ResetPassword()
