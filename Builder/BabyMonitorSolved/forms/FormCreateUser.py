from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length

class FormCreateUser(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=4, max=16)])
    password_confirm = PasswordField('Confirm your password', validators=[Length(min=4, max=16)])
    role = SelectField('Role', choices=[])

    type_form_user = HiddenField('user', default='userstation')
    submit_create_user = SubmitField('Save')