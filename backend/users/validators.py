from django.core.validators import RegexValidator
from rest_framework.serializers import ValidationError


def combined_username_validator(value):

    regex_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message='Username contains restricted symbols. Please use only '
                'letters, numbers and .@+- symbols.',
    )
    regex_validator(value)

    if value == 'me':
        raise ValidationError('Username "me" is not allowed.')
