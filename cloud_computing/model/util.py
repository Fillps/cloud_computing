# -*- coding: utf-8 -*-
from wtforms.fields import TextField


class ReadonlyTextField(TextField):
    """Create a read-only text field."""
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyTextField, self).__call__(*args, **kwargs)