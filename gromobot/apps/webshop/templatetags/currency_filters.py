from decimal import Decimal as D
from decimal import InvalidOperation

from babel.numbers import format_currency, get_currency_symbol
from django import template
from django.conf import settings
from django.utils.translation import get_language, to_locale

register = template.Library()


@register.filter(name="currency")
def currency(value, currency_format=None):
    """
    Format decimal value as currency
    """
    if currency_format is None:
        currency_format = settings.DEFAULT_CURRENCY

    try:
        value = D(value)
    except (TypeError, InvalidOperation):
        return ""
    # Using Babel's currency formatting
    # http://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency
    CURRENCY_FORMAT = getattr(settings, "CURRENCY_FORMAT", None)
    kwargs = {
        "currency": currency_format,
        "locale": to_locale(get_language() or settings.LANGUAGE_CODE),
    }
    if isinstance(CURRENCY_FORMAT, dict):
        kwargs.update(CURRENCY_FORMAT.get(currency_format, {}))
    else:
        kwargs["format"] = CURRENCY_FORMAT
    return format_currency(value, **kwargs)


@register.filter(name="formate_price")
def formate_price(value):
    """
    Format decimal value as currency
    """
    try:
        value = D(value)
    except (TypeError, InvalidOperation):
        return ""

    return int(value)


@register.simple_tag
def currency_symbol(currency):
    """
    Format decimal value as currency
    """
    return get_currency_symbol(
        currency, to_locale(get_language() or settings.LANGUAGE_CODE)
    )
