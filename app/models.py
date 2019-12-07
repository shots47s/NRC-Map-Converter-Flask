from flask import current_app
from flask_user import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.orm.collections import attribute_mapped_collection
from app import db
from app.oauth import OAuth_pretty
import redis
import rq
from time import time
import json

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
  notifications = db.relationship('Notification', backref='users',
                                  lazy='dynamic')

  tasks = db.relationship('Task', backref='users', lazy='dynamic')

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

  def add_notification(self, name, data):
    import json
    self.notifications.filter_by(name=name).delete()
    print("adding HERE")
    n = Notification(name=name, payload_json=json.dumps(data), users=self)
    print("Made it")
    db.session.add(n)
    print("Added")
    return n

  def launch_task(self, name, description, batch_id, *args, **kwargs):
    print("args = {}".format(*args))
    rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id, batch_id,
                                            *args, **kwargs)
    print("LT: {} {} {} {} {}".format(name,self.id, batch_id, *args, **kwargs))
    task = Task(id=rq_job.get_id(), name=name, description=description,
                users=self, batch_id=batch_id)

    db.session.add(task)
    return task

  def get_tasks_in_progress(self):
    return Task.query.filter_by(users=self, complete=False).all()

  def get_task_in_progress(self, name):
    return Task.query.filter_by(name=name, users=self, complete=False).first()

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
  contents = db.Column(db.Text)
  deployed = db.Column(db.Boolean, default=False)

  def set_deployed(self):
    self.deployed = True
    print("------------setting deployed")
    db.session.commit()

  def __repr__(self):
    return '<Excel File id = {}, name = {}, filename = {}, user_id = {}>'\
           .format(self.id, self.name, self.file_name,self.user_id)

#Notification Model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


# Task Model
class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    complete = db.Column(db.Boolean, default=False)
    batch_id = db.Column(db.String(10))

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100

    def is_job_done(self):
      job = self.get_rq_job()
      return job.is_finished if job is not None else True

    def signal_completed(self):
      print("singalling complete!!!! {}".format(self.id))
      self.complete = True
      db.session.commit()
