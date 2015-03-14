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


class BOOTSTRAPFORM(SQLFORM):
    SQLFORM.widgets.string = LimitStringWidget
    SQLFORM.widgets.text = LimitTextWidget

    def __init__(self, table, *args, **kwargs):
        super(BOOTSTRAPFORM, self).__init__(table, *args, formstyle='bootstrap3_stacked', **kwargs)

    def process(self, *args, **kwargs):
        if ('beforevalidation' in kwargs):
            call_as_list(kwargs['beforevalidation'], self)

        return super(BOOTSTRAPFORM, self).process(**kwargs)

    def getFieldRequirements(self, fieldname):

        field = (self.table[fieldname] if fieldname in self.table.fields
                 else self.extra_fields[fieldname])
        requires = field.requires or []
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        return requires

    @staticmethod
    def factory(*fields, **kwargs):
        return BOOTSTRAPFORM(DAL(None).define_table("no_table",
                                                 *fields), **kwargs)

    @staticmethod
    def confirm(text='OK', btntype="btn-default", buttons=None, hidden=None):
        if not buttons:
            buttons = {}
        if not hidden:
            hidden = {}
        inputs = [INPUT(_type='button',
                        _value=name,
                        _class='btn btn-default',
                        _onclick=FORM.REDIRECT_JS % link)
                  for name, link in buttons.iteritems()]
        inputs += [INPUT(_type='hidden',
                         _name=name,
                         _value=value)
                   for name, value in hidden.iteritems()]
        form = FORM(INPUT(_type='submit', _value=text, _class='btn {0}'.format(btntype)), *inputs,
                    formstyle='bootstrap3_stacked')
        form.process()
        return form