from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired

class UploadExcelFile(FlaskForm):
  name = StringField("Name",
                   validators=[DataRequired('Please give a human readable name to this file.')])
  file_name = FileField('Excel File',
                        validators=[FileRequired('Please select a File')])

