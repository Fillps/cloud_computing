# -*- coding: utf-8 -*-
import calendar
import datetime

from wtforms import TextAreaField, IntegerField
from wtforms.widgets import TextArea


class CKTextAreaWidget(TextArea):
    """Rich text editor for resource requests."""

    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    """Wrapper for the text editor."""
    widget = CKTextAreaWidget()


class ReadonlyCKTextAreaField(CKTextAreaField):
    """Read-only version of the CKTWidget."""

    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readOnly', True)
        return super(CKTextAreaField, self).__call__(*args, **kwargs)


class ReadOnlyIntegerField(IntegerField):
    """Read-only integer field."""

    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readOnly', True)
        return super(IntegerField, self).__call__(*args, **kwargs)


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)

