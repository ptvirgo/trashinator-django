from django.core.exceptions import ValidationError


def zero_or_more(num):
    if not num >= 0:
        raise ValidationError("must be >= 0")


def one_or_more(num):
    if not num >= 1:
        raise ValidationError("must be >= 1")
