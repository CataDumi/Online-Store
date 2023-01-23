from flask_wtf import FlaskForm, Form
from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators, TextField, TextAreaField, \
    IntegerField
from wtforms.validators import DataRequired, URL, InputRequired, NumberRange, Email,Length


class EditForm(FlaskForm):
    name = StringField('Edit book name', validators=[DataRequired()])
    author = StringField('Edit author name', validators=[DataRequired()])
    quantity = IntegerField('Edit quantity available ', validators=[DataRequired()])
    price = IntegerField('Edit book price', validators=[DataRequired()])
    rating = IntegerField('Edit book rating', validators=[DataRequired(), NumberRange(min=0, max=5)])
    url = TextField('Edit url', validators=[DataRequired(), URL()])
    description = TextAreaField('Edit book description', validators=[DataRequired()])
    submit = SubmitField('Submit')

#Form pt inregistrare users
class RegisterForm(FlaskForm):
    name = StringField('Enter name', validators=[DataRequired()])
    email = TextField('Enter email', validators=[DataRequired(),Email()])
    password = PasswordField('Enter password', validators=[DataRequired(),Length(min=4)])
    password_confirmation = PasswordField('Confirm password', validators=[DataRequired(),Length(min=4)])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = TextField('Enter email', validators=[DataRequired(), Email()])
    password = PasswordField('Enter password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Submit')
