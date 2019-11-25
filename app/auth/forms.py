from flask_wtf import FlaskForm
from flask_user.forms import RegisterForm
from flask_user import UserManager
from wtforms import StringField, SubmitField, SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired,Required, ValidationError
from flask_user.forms import password_validator
from app import db
from app.models import Role

# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields

class RoleMultiField(SelectMultipleField):

  def pre_validate(self,form):
    pass


class CustomRegisterForm(RegisterForm):
  first_name = StringField('First name', validators=[
      DataRequired('First name is required')])
  last_name = StringField('Last name', validators=[
      DataRequired('Last name is required')])
  roles = RoleMultiField('Roles',
                          widget=ListWidget(prefix_label=True))

  def validate_roles(form,field):
    if field.data is None or len(field.data) == 0:
      raise ValidationError("Need to specify at least one role")
  #roles = QuerySelectMultipleField("Roles",
  #  query_factory=lambda: Role.query,
  #  validators=[DataRequired('Must Select at least one role')])
  submit = SubmitField('Save')

# Define the User profile form
class UserProfileForm(FlaskForm):
  first_name = StringField('First name', validators=[
      DataRequired('First name is required')])
  last_name = StringField('Last name', validators=[
      DataRequired('Last name is required')])

  roles = RoleMultiField('Roles',
                          widget=ListWidget(prefix_label=True),)
  submit = SubmitField('Save')

  def validate_roles(form,field):
    if field.data is None or len(field.data) == 0:
      raise ValidationError("Need to specify at least one role")


class CustomUserManager(UserManager):

  def customize(self,app):
    self.RegisterFormClass = CustomRegisterForm
