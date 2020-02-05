from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length

class FormLogin(FlaskForm):
    username_login = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password_login = PasswordField('Password', validators=[DataRequired()])
    remember_me_login = BooleanField('Keep me logged in')
    type_form_login = HiddenField('login', default='login')
    submit_login = SubmitField('Log In')