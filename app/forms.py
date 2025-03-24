from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, DateField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from .models import User
from flask_wtf.file import FileAllowed, FileRequired


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=12,message='Das Passwort muss mindestens 8 Zeichen lang sein.'),
                Regexp(
            r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
            message='Das Passwort muss mindestens einen Grossbuchstaben, eine Zahl und ein Sonderzeichen enthalten.'
        )
        ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AddItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    room = StringField('Room')
    cost = FloatField('Cost')
    bought_by = StringField('Bought By')
    purchase_date = DateField('Purchase Date', format='%Y-%m-%d')  # Specify format
    is_new = BooleanField('New')
    category = SelectField('Category', choices=[
        ('furniture', 'Furniture'),
        ('electronic', 'Electronic Device'),
        ('tools', 'Tools'),
        ('other', 'Other')
    ])
    image = FileField('Item Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Add Item')

class EditItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    room = StringField('Room')
    cost = FloatField('Cost')
    bought_by = StringField('Bought By')
    purchase_date = DateField('Purchase Date', format='%Y-%m-%d')
    is_new = BooleanField('New')
    category = SelectField('Category', choices=[
        ('furniture', 'Furniture'),
        ('electronic', 'Electronic Device'),
        ('tools', 'Tools'),
        ('other', 'Other')
    ])
    image = FileField('Item Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Update Item')
