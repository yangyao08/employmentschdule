from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, NumberRange, optional, InputRequired 
from app.models import User
#from datetime import datetime
from app import db, login
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log in')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('The username is taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The email is already registered.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Username is taken. Please use a different username.')

class RequiredIf(InputRequired):
    field_flags = ('requiredif',)

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Error('' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class AddPersonForm(FlaskForm):
    Name = StringField('Enter the name', validators=[DataRequired()])
    Position = StringField('Enter his/her position', validators=[DataRequired()])
    #Tier = StringField('Enter his job tier', validators=[DataRequired()])
    #Engagements = StringField('Enter his current engagements')
    #Easy_Jobs = IntegerField('Enter the current number of easy jobs the personnel has',validators=[InputRequired(),NumberRange(min=0, max=100),optional()])
    #Medium_Jobs = IntegerField('Enter the current number of medium jobs the personnel has',validators=[InputRequired(),NumberRange(min=0, max=100),optional()])
    #Difficult_Jobs = IntegerField('Enter the current number of difficult jobs the personnel has',validators=[InputRequired(),NumberRange(min=0, max=100),optional()])
    #Employed = 1
    submit = SubmitField('Add')


class AddEngagementForm(FlaskForm):
    Name = StringField('Enter the job name', validators=[DataRequired()])
    Job = StringField('Enter the job type', validators=[DataRequired()])
    Difficulty = IntegerField('Enter the difficulty of job',validators=[InputRequired(),NumberRange(min=1, max=3),optional()],render_kw={"placeholder": "1-Easy,2-Medium,3-Hard"})
    Expected_Hours = IntegerField('Enter the expected hours',validators=[InputRequired(),NumberRange(min=0, max=1000),optional()])
    Start_Date = DateField('Enter the start date',format='%Y-%m-%d')
    End_Date = DateField('Enter the deadline of this project',format='%Y-%m-%d')
    Days_Given = IntegerField('Enter the number of days given',validators=[InputRequired(),NumberRange(min=0, max=1000),optional()])
    Req_person = IntegerField('Enter the number of personnel required',validators=[InputRequired(),NumberRange(min=1, max=100),optional()])
    #Personnel_Involved= IntegerField('Enter Module 1 ratings', validators=[DataRequired()])
    Priority_Person = StringField('Enter any priority person')
    #Completed = IntegerField('Enter the current number of easy jobs the personnel has')
    submit = SubmitField('Add')

class RemovePersonForm(FlaskForm):
    person = StringField("Enter the name of the person you want to remove",validators=[DataRequired()])
    submit = SubmitField("Submit")

class RemoveEngagementForm(FlaskForm):
    engagement = StringField("Enter the name of the job you want to remove",validators=[DataRequired()])
    submit = SubmitField("Submit")

class SearchPersonnelForm(FlaskForm):
    Personnel = StringField('Enter Person Name', validators=[DataRequired()])
    submit = SubmitField('Search')

class SearchEngagementForm(FlaskForm):
    Engagement = StringField('Enter Job Name', validators=[DataRequired()])
    submit = SubmitField('Search')

class AssignEngagementForm(FlaskForm):
    Engagement = StringField("Enter engagement to be assigned.",validators=[DataRequired()])
    submit = SubmitField("Assign")