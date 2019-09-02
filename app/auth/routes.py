from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_user import current_user, login_required, roles_accepted
from app import db
from app.auth import auth_bp
from app.models import User, Role, UsersRoles
from app.auth.forms import UserProfileForm, CustomRegisterForm
from datetime import datetime

@auth_bp.route('/auth/admin')
@roles_accepted('admin')
def admin_page():
  return render_template('auth/admin/users.html')

@auth_bp.route('/auth/users')
@roles_accepted('admin')
def user_admin_page():
  users = User.query.all()
  return render_template('auth/admin/users.html',users=users, admin=True)

@auth_bp.route('/auth/create_user', methods=['GET', 'POST'])
@roles_accepted('admin')
def create_user_page():
  form = CustomRegisterForm(form=request.form, obj=None)
  ## get Roles
  roles = Role.query.all()
  form.roles.choices = [(r.id, r.name) for r in roles]

  if request.method == 'POST' and form.validate():
      user = User.query.filter(User.email == request.form['email']).first()
      if not user:
        user = User(email=request.form['email'],
                    first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    password=current_app.user_manager.hash_password(request.form['password']),
                    active=True,
                    email_confirmed_at=datetime.utcnow())

        for r in form.roles.data:
          user.roles.append(Role.query.filter(Role.id==r).first())

        db.session.add(user)
        db.session.commit()
      else:
        flash("User already exists")

      return redirect(url_for('auth.user_admin_page')) #!!! check
  return render_template('auth/admin/create_user.html',form=form,admin=True)

@auth_bp.route('/auth/delete_user', methods=['GET'])
@roles_accepted('admin')
def delete_user_page():
  ### add error checking
  try:
    user_id = request.args.get('user_id')

    db.session.query(UsersRoles).filter_by(user_id = user_id).delete()
    db.session.query(User).filter_by(id = user_id).delete()
    db.session.commit()

    flash('You successfully deleted this user') ### !!! Add user name to this
    return redirect(url_for('auth.user_admin_page')) ### !!! check this
  except Exception as e:
    flash('Somthing unexpected happened. This error has been logged: {}'.format(str(e)),'error')
    return redirect(request.referrer)

@auth_bp.route('/auth/profile', methods=['GET','POST'])
@roles_accepted('admin','member')
def user_profile_page():
  roleNames = Role.query.all()
  user = User.query.filter(User.id==request.args.get('user_id')).first()
  if user is None:
    ## Replace with Previous
    redirect(url_for('auth.user_admin_page'))

  form = UserProfileForm(request.form, obj=user)
  roles = Role.query.all()
  form.roles.choices = [(r.id, r.name) for r in roles]
  current_roles = [r.id for r in user.roles]

  session['login_next_url'] = url_for('auth.user_profile_page',user_id=user.id)

  if request.method == 'POST' and form.validate():
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']

    user.roles = []
    for r in form.roles.data:
        user.roles.append(Role.query.filter(Role.id==r).first())
    db.session.commit()

    return redirect(url_for('auth.user_admin_page'))

  # for GET or Invalid POST
  return render_template('auth/user_profile.html',
                          current_user=current_user,
                          form_user=user,
                          current_roles=current_roles,
                          form=form, admin=True)

