import os
import click
from datetime import datetime

#from app.models import User,Role,UserRoles
#from app import db,current_app

def register(app):

  @app.cli.command("seed_db")
  def seed_db():
    from app import db
    from app.models import User, Role, UsersRoles

    user = User(first_name="admin",
                last_name="admin",
                email="admin@example.com",
                email_confirmed_at=datetime.utcnow(),
                active=True,
                password=app.user_manager.hash_password('Password1'))

    user.roles.append(Role(name="admin"))
    user.roles.append(Role(name="member"))

    db.session.add(user)
    db.session.commit()
