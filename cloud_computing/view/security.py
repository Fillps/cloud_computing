from flask_security.forms import RegisterForm, Required
from wtforms import StringField
from wtforms.validators import Length, Optional


class ExtendedRegisterForm(RegisterForm):
    name = StringField('Nome', [Required()])
    last_name = StringField('Sobrenome', [Required()])
    cpf = StringField('CPF', [Length(11, 11), Optional()])
    cnpj = StringField('CNPJ', [Length(14, 14), Optional()])
    company = StringField('Empresa', [Optional()])

