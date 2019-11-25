import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
      'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    MAIL_SERVER         = os.environ.get('MAIL_SERVER')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS        = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = '"Shawn Brown" <shawntbrown@gmail.com>'
    ADMINS              = ['shawntbrown@gmail.com']
    LOG_TO_STDOUT       = True


    LANGUAGES = ['en', 'fr']

    #Flask-User Settings

    USER_APP_NAME = "NRC Map"
    USER_ENABLE_CHANGE_PASSWORD   = True
    USER_ENABLE_CHANGE_USERNAME   = False
    USER_ENABLE_CONFIFM_EMAIL     = True
    USER_ENABLE_FORGOT_PASSWORD   = True
    USER_ENABLE_EMAIL             = True
    USER_ENABLE_REGISTRATION      = True
    USER_REQUIRE_RETYPE_PASSWORD  = True
    USER_ENABLE_USERNAME          = False
    USER_AFTER_LOGIN_ENDPOINT     = "main.index"
    USER_AFTER_LOGOUT_ENDPOINT    = "main.index"
    USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL = False
    USER_LOGIN_TEMPLATE           = "auth/flask_user/login.html"
    USER_FORGOT_PASSWORD_TEMPLATE = "auth/flask_user/forgot_password.html"
    USER_REGISTER_TEMPLATE        = "auth/flask_user/register.html"

    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    OAUTHLIB_INSECURE_TRANSPORT = os.environ.get("OAUTHLIB_INSECURE_TRANSPORT")

    ORCID_OAUTH_CLIENT_ID = os.environ.get("ORCID_OAUTH_CLIENT_ID")
    ORCID_OAUTH_CLIENT_SECRET = os.environ.get("ORCID_OAUTH_CLIENT_SECRET")

    ## EXCEL FILE UPLOAD PARAMETERS
    UPLOAD_DEFAULT_DEST = os.path.join(basedir,'/static/fileuploads')
    UPLOAD_DEFAULT_URL = "/static/fileuploads"

    UPLOADED_EXCELS_DEST = os.path.join(basedir,'app/static/excel-file-uploads')
    UPLOADED_DEFAULT_URL = "/static/excel-file-uploads"
    EXCEL_ALLOWED_EXTENSIONS = set(['xls','xslx','csv'])

    ## Google Maps API
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")



