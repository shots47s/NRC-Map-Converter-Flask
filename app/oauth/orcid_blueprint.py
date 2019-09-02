from flask import flash, redirect, session
from flask_user import current_user
from flask_login import login_user
from app.oauth.orcid import make_orcid_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from app.models import db, User, OAuth, Role, UsersRoles
from datetime import datetime
from config import Config
from pprint import pprint


orcid_blueprint = make_orcid_blueprint(
  storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
)

@oauth_authorized.connect_via(orcid_blueprint)
def orcid_logged_in(orcid_blueprint, token):

  ## Check if I have an API token

  if not token:
    flash("Failed to log in.", category="error")
    return False

  print(token.items())

  ## get the orcid id information
  ## ORCID API calls require that the orcid id be in the request, so that needs
  ## to be extracted from the token prior to making any requests
  orcid_user_id = token['orcid']

  response = orcid_blueprint.session.get("{}/record".format(orcid_user_id))

  if not response.ok:
    flash("Failed to get ORCID User Data", category="error")
    return False

  orcid_record = response.json()
  pprint(orcid_record)

  # Find this OAuth in the
  query = OAuth.query.filter_by(
    provider=orcid_blueprint.name,provider_user_id=orcid_user_id)
  try:
    oauth = query.one()
  except NoResultFound:
    oauth = OAuth(
      provider=orcid_blueprint.name,
      provider_user_id=orcid_user_id,
      provider_user_login=orcid_user_id,
      token=token)


  if current_user.is_anonymous:
    if oauth.user:
      login_user(oauth.user)
      flash("Successfully logged in through ORCID")
    else:
      orcid_person = orcid_record['person']

      ### check if there is a user with this email address
      # Check to see if the ORCID user has an email exposed, otherwise, we cannot use it
      # if not orcid_record['person']['emails']
      if len(orcid_person['emails']['email']) == 0:
        flash("Failed to create new user, must have at least one ORCID email address accessible to restricted")
        return False

      orcid_email = orcid_person['emails']['email'][0]['email']

      query = User.query.filter_by(email=orcid_email)
      try:
        nrc_u = query.one()
        oauth.user = nrc_u
        db.session.add(oauth)
        db.session.commit()
        login_user(oauth.user)

      except NoResultFound:
        # create a new user

        user = User(email=orcid_person['emails']['email'][0]['email'],
                    first_name = orcid_person['name']['given-names']['value'],
                    last_name = orcid_person['name']['family-name']['value'],
                    active=True,
                    email_confirmed_at=datetime.utcnow())

        user.roles.append(Role.query.filter(Role.name=="member").first())
        oauth.user = user

        db.session.add_all([user,oauth])
        db.session.commit()

        login_user(user)
  else:
    if oauth.user:
      flash ("Account already associated with another user")
    else:
      oauth.user = current_user
      db.session.add(oauth)
      db.session.commit()
      flash("Successfully linked ORCID account")

  return False

@oauth_authorized.connect
def redirect_to_next_url(orcid_blueprint, token):
    # retrieve `next_url` from Flask's session cookie
    if session.get('login_next_url') is not None:
      next_url = session["login_next_url"]

    # redirect the user to `next_url`
      return redirect(next_url)

 #notify on OAuth provider error
@oauth_error.connect_via(orcid_blueprint)
def orcid_error(orcid_blueprint,**kwargs):
  msg = "OAuth error from {name}! ".format(name=orcid_blueprint.name)
  for k,v in kwargs.items():
    msg += "{} = {} ".format(k,str(v))
  print("msg= {}".format(msg))
  flash(msg, category="error")

