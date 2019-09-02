from flask import Blueprint

util_bp = Blueprint('util',__name__,template_folder='../templates')

from app.util import filters
