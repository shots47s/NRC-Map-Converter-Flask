from flask import Blueprint
from flask_uploads import UploadSet, configure_uploads

excel_bp = Blueprint('excel',__name__,template_folder='../templates')

from app.excel import routes
