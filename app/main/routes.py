from flask import render_template, flash, redirect, url_for, request, current_app, session
from flask_user import current_user, login_required, roles_accepted
from app import db
from app.main import main_bp
from config import Config

@main_bp.route('/', methods=['GET', 'POST'])
@main_bp.route('/index', methods=['GET', 'POST'])
def index():
  ## ensure that the login_next_url is none
  session['login_next_url'] = None
  if not current_user.is_authenticated:
    return redirect(url_for('user.login'))
  admin=False
  if current_user.has_role("admin"):
    admin=True

  return render_template('index.html', title="Home", admin=admin)


