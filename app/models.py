from flask_user import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.orm.collections import attribute_mapped_collection
from app import db
from app.oauth import OAuth_pretty

class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)

  # User authentication information (required for Flask-User)
  email = db.Column(db.String(255), nullable=False, server_default='', unique=True)
  email_confirmed_at = db.Column(db.DateTime())
  password = db.Column(db.String(255), nullable=False, server_default='')
  # reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
  active = db.Column(db.Boolean(), nullable=False, server_default='0')

  # User information
  active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
  first_name = db.Column(db.String(50), nullable=False, server_default='')
  last_name = db.Column(db.String(50), nullable=False, server_default='')

  # Relationships
  roles = db.relationship('Role', secondary='users_roles',
                          backref=db.backref('users', lazy='dynamic'))

  def has_role(self, role):
    for item in self.roles:
      if item.name == 'admin':
        return True
    return False

  def role(self):
    for item in self.roles:
      return item.name

  def name(self):
    return self.first_name + " " + self.last_name

  def oauths(self):
    o = OAuth.query.filter(OAuth.user==self).all()
    return [(x.provider,x.provider_user_login,OAuth_pretty[x.provider]) for x in o]


# Define the Role data model
class Role(db.Model):
  __tablename__ = 'roles'
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(50), nullable=False, server_default='', unique=True)  # for @roles_accepted()
  label = db.Column(db.String(255), server_default='')  # for display purposes

  def __repr__(self):
    return self.name

# Define the UserRoles association model
class UsersRoles(db.Model):
  __tablename__ = 'users_roles'
  id = db.Column(db.Integer(), primary_key=True)
  user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
  role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

# OAUTH Model
class OAuth(OAuthConsumerMixin, db.Model):
  __table_args__ = (db.UniqueConstraint("provider", "provider_user_id"),)
  provider_user_id = db.Column(db.String(256), nullable=False)
  provider_user_login = db.Column(db.String(256), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id),nullable=False)
  user = db.relationship(User,
                         backref=db.backref("oauth",
                                            collection_class=attribute_mapped_collection('provider'),
                                            cascade="all, delete-orphan")
                         )

# Excel files Model
class ExcelFiles(db.Model):
  __tablename__ = "excel_files"
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(255), nullable=False, server_default='')
  file_name = db.Column(db.String,default=None, nullable=False)
  file_url = db.Column(db.String)
  valid = db.Column(db.Boolean, server_default='0', nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id),nullable=False)


  def __repr__(self):
    return '<Excel File id = {}, name = {}, filename = {}, user_id = {}>'\
           .format(self.id, self.name, self.file_name,self.user_id)




