from flask import flash
from flask_user import current_user
from flask_login import login_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, ouath_error
from flask_dance consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from app.models import db, User, QAuth

blueprint = make_google_blueprint(
  scope=["profile","email"],
  storage=SQLAlchemyStorage(OAuth, db.session, user=current_user))


@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):

  ## Check if I have an API token

  if not token:
    flash("Failed to log in.", category="error")
    return False


  ## Get this blueprints session
  response = blueprint.session.get("/oauth2/v2/userinfo")
  if not response.ok:
    flash("Failed to fetch the user info from session", category="error")
    return False

  google_info = response.json()
  google_user_id = google_info["id"]

  # Find this OAuth token in the database, or create it
  query = OAuth.query.filter_by(
    provider=blueprint.name, provider_user_id=google_user_id
  )
  try:
    oauth = query.one()
  except NoResultFound:
    google_user_login = str(google_info["email"])
    oauth = OAuth(
      provider=blueprint.name,
      provider_user_id=google_user_id,
      provider_user_login=google_user_login,
      token=token,
    )

  if oauth.user:
    login_user(oauth.user)
    flash("Successfully logged in through Google")
  else:
    print(dir(google_info))
    #user = User(email=google_info["email"], first_name=google_info["name"])

