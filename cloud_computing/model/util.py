# -*- coding: utf-8 -*-
from wtforms import TextAreaField
from wtforms.widgets import TextArea


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class ReadonlyCKTextAreaField(CKTextAreaField):
    """Create a read-only text field."""

    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readOnly', True)
        return super(CKTextAreaField, self).__call__(*args, **kwargs)
