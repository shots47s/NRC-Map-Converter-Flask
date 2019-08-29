from __future__ import unicode_literals

import os.path
from urlobject import URLObject
from oauthlib.oauth1 import SIGNATURE_RSA
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask_dance.consumer.requests import OAuth2Session
from functools import partial
from flask.globals import LocalProxy, _lookup_app_object

try:
  from flask import _app_ctx_stack as stack
except ImportError:
  from flask import _request_ctx_stack as stack


__maintainer__ = "Shawn T. Brown <stbrown@mcin.ca>"

class JsonOath2Session(OAuth2Session):
  def __init__(self, *args, **kwargs):
    super(JsonOath2Session, self).__init__(*args, **kwargs)
    print("setting Headers")
    self.headers["Accept"] = "application/orcid+json"


def make_orcid_blueprint(
  client_id=None,
  client_secret=None,
  scope=None,
  offline=False,
  redirect_url=None,
  redirect_to=None,
  login_url=None,
  authorized_url=None,
  session_class=None,
  storage=None,
):
  scope = scope or ["/authenticate","/read-limited"]
  session_class = session_class or JsonOath2Session

  orcid_bp = OAuth2ConsumerBlueprint(
    "orcid",
    __name__,
    client_id=client_id,
    client_secret=client_secret,
    scope=scope,
    base_url="https://api.sandbox.orcid.org/v2.0",
    token_url="https://api.sandbox.orcid.org/oauth/token",
    authorization_url="https://sandbox.orcid.org/oauth/authorize",
    redirect_url=redirect_url,
    redirect_to=redirect_to,
    login_url=login_url,
    authorized_url=authorized_url,
    session_class=session_class,
    storage=storage
    )

  orcid_bp.from_config["client_id"] = "ORCID_OAUTH_CLIENT_ID"
  orcid_bp.from_config["client_secret"] = "ORCID_OAUTH_CLIENT_SECRET"

  print(dir(orcid_bp))
  @orcid_bp.before_app_request
  def set_applocal_session():
    ctx = stack.top
    ctx.orchid_oauth = orcid_bp.session

  #@orcid_bp.after_request
  #def get_the_token(response):
  #  pass
  #  #print("shit")


  return orcid_bp


orcid = LocalProxy(partial(_lookup_app_object, "orcid_oauth"))
