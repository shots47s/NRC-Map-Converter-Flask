from datetime import datetime
import os

from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, UserMixin
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_uploads import configure_uploads
from config import Config

db = SQLAlchemy()
csrf_protect = CSRFProtect()
mail = Mail()
migrate = Migrate()
bootstrap = Bootstrap()

def create_app(config_settings=Config):

  app = Flask(__name__, static_url_path='/static')
  app.config.from_object(config_settings)

  db.init_app(app)
  migrate.init_app(app, db)
  mail.init_app(app)
  csrf_protect.init_app(app)
  bootstrap.init_app(app)

  from app.util import filters

  from wtforms.fields import HiddenField

  def is_hidden_field_filter(field):
    return isinstance(field,HiddenField)

  app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

  from app.auth import auth_bp
  app.register_blueprint(auth_bp)

  from app.util import util_bp
  app.register_blueprint(util_bp)

  from app.excel import excel_bp
  app.register_blueprint(excel_bp)

  from app.excel.routes import excels
  configure_uploads(app, excels)

  from app.oauth.google_blueprint import google_blueprint
  app.register_blueprint(google_blueprint, url_prefix="/login")

  from app.oauth.orcid_blueprint import orcid_blueprint
  app.register_blueprint(orcid_blueprint, url_prefix="/login")

  from app.main import main_bp
  app.register_blueprint(main_bp)

  from app.models import User
  from app.auth.forms import CustomUserManager

  user_manager = CustomUserManager(app, db, User)

  @app.context_processor
  def context_processor():
    return dict(user_manager=user_manager)

  ### Initialize Email
  init_email_and_logs_error_handler(app)

  return app

### Function to initialize the email and logs
def init_email_and_logs_error_handler(app):
  if app.debug and not app.testing: return

  import logging
  from logging.handlers import SMTPHandler

  if app.config['MAIL_SERVER']:
    auth = None

    if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
      auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

      secure = None
      if app.config['MAIL_USE_TLS']:
        secure = 90

      mail_handler = SMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
          fromaddr='no-reply@' + app.config['MAIL_SERVER'],
          toaddrs=app.config['ADMINS'], subject='Microblog Failure',
          credentials=auth, secure=secure)
      mail_handler.setLevel(logging.ERROR)
      app.logger.addHandler(mail_handler)

      if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
      else:
        if not os.path.exists('logs'):
          os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

      app.logger.setLevel(logging.INFO)
      app.logger.info('NRC Mapping startup')

