from flask import flash
from flask_user import current_user
from flask_login import login_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from app.models import db, User, OAuth, Role, UsersRoles
from datetime import datetime

google_blueprint = make_google_blueprint(
  storage=SQLAlchemyStorage(OAuth, db.session, user=current_user),
  scope=['https://www.googleapis.com/auth/userinfo.email','openid',
         'https://www.googleapis.com/auth/userinfo.profile']
)

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(google_blueprint, token):

  ## Check if I have an API token

  if not token:
    flash("Failed to log in.", category="error")
    return False


  ## Get this blueprints session
  response = google_blueprint.session.get("/oauth2/v2/userinfo")
  if not response.ok:
    flash("Failed to fetch the user info from session", category="error")
    return False

  google_info = response.json()
  google_user_id = google_info["id"]

  # Find this OAuth token in the database, or create it
  query = OAuth.query.filter_by(
    provider=google_blueprint.name, provider_user_id=google_user_id
  )
  try:
    oauth = query.one()
  except NoResultFound:
    google_user_login = str(google_info["email"])
    oauth = OAuth(
      provider=google_blueprint.name,
      provider_user_id=google_user_id,
      provider_user_login=google_user_login,
      token=token,
    )

  if current_user.is_anonymous:
    if oauth.user:
      print("We are funcking here")
      login_user(oauth.user)
      flash("Successfully logged in through Google")
    else:
      print("Why is there no oauth")
      ### No user, so create a user
      user = User(email=google_info['email'],
                  first_name=google_info['given_name'],
                  last_name=google_info['family_name'],
                  active=True,
                  email_confirmed_at=datetime.utcnow())
      ### make the user a member
      user.roles.append(Role.query.filter(Role.name=="member").first())
      oauth.user = user

      db.session.add_all([user,oauth])
      db.session.commit()



      login_user(user)
      flash("Successfully signed in with Google.")
  else:
    if oauth.user:
      pass

    else:
      oauth.user = current_user
      db.session.add(oauth)
      db.session.commit()
      flash("Successfully linked to Google Account")

  return False



# notify on OAuth provider error
@oauth_error.connect_via(google_blueprint)
def google_error(googe_blueprint,**kwargs):
  msg = "OAuth error from {name}! ".format(name=google_blueprint.name)
  for k,v in kwargs.items():
    msg += "{} = {}".format(k,str(v))
  print("msg= {}".format(msg))
  flash(msg, category="error")
