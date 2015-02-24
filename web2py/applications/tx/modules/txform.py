from gluon.sqlhtml import FormWidget
from gluon.sqlhtml import StringWidget
from gluon.validators import IS_LENGTH
from gluon import TEXTAREA, INPUT, SQLFORM
from gluon.validators import Validator, FieldMethod, FieldVirtual
from gluon.sqlhtml import formstyle_bootstrap3_stacked
from gluon.sqlhtml import Field
from gluon.html import call_as_list
from gluon import DAL
from gluon import FORM

class LimitTextWidget(FormWidget):
    _class = 'text'

    @classmethod
    def widget(cls, field, value, **attributes):
        size = 0
        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        for req in requires:
            if isinstance(req, IS_LENGTH):
                size = req.maxsize
            pass

        default = dict(value=value)
        attr = cls._attributes(field, default, **attributes)

        if (size > 0 and size < 500):
            attr['_rows'] = 3
            attr['_maxlength'] = size

        outstr = TEXTAREA(**attr)

        return outstr


class LimitStringWidget(FormWidget):
    _class = 'input'

    @classmethod
    def widget(cls, field, value, **attributes):
        size = 0
        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        for req in requires:
            if isinstance(req, IS_LENGTH):
                size = req.maxsize
            pass

        default = dict(value=value)
        attr = cls._attributes(field, default, **attributes)

        if (size > 0 and size < 500):
            attr['_maxlength'] = size

        return INPUT(**attr)


class BOOTUPFORM(SQLFORM):
    SQLFORM.widgets.string = LimitStringWidget
    SQLFORM.widgets.text = LimitTextWidget

    def __init__(self, table, *args, **kwargs):
        super(BOOTUPFORM, self).__init__(table, *args, formstyle='bootstrap3_stacked', **kwargs)

    def process(self, *args, **kwargs):
        if ('beforevalidation' in kwargs):
            call_as_list(kwargs['beforevalidation'], self)

        return super(BOOTUPFORM, self).process(**kwargs)

    def getFieldRequirements(self, fieldname):

        field = (self.table[fieldname] if fieldname in self.table.fields
                 else self.extra_fields[fieldname])
        requires = field.requires or []
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        return requires

    @staticmethod
    def factory(*fields, **kwargs):
        return BOOTUPFORM(DAL(None).define_table("no_table",
                                                 *fields), **kwargs)