# -*- coding: utf-8 -*-
import os
from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask import send_from_directory
from flask_user import current_user
from flask_uploads import UploadSet,UploadNotAllowed
import pyexcel as p
from app.excel import excel_bp
from app.excel.forms import UploadExcelFile
from app.models import ExcelFiles
from app import db
from app.excel.nrc2bivisio import validate_headers_from_excel,nrc2bivisio
excels = UploadSet('excels', tuple('xls xlsx csv'.split()))

@excel_bp.route('/excel/upload',methods=['GET','POST'])
def upload_excel_file():
  form = UploadExcelFile(form = request.form, obj=None)
  if request.method == 'POST':
    if form.validate_on_submit():
      ## Check if the name already exists
      xFs = [x.name for x in ExcelFiles.query.all()]
      if request.form['name'] in xFs:
        flash("There is already a file with the name {}".format(request.form['name']))
      else:
        #return redirect(url_for('excel.upload_excel_file'))
        excel_filename = request.files['file_name']
        try:
          excel_file = excels.save(request.files['file_name'])
        except UploadNotAllowed:
          flash('Please only upload excel files (xls, xlsx, csv)')
        else:
          # Check if this is a valid NRC file
          passing,msgs = validate_headers_from_excel(os.path.join(current_app.config['UPLOADED_EXCELS_DEST'],
                                                                  excel_file))
          if passing == 'ERROR':
            for msg in msgs:
              flash(msg)
            return redirect(request.referrer)
          else:
            excel_file = ExcelFiles(
                                    name = request.form['name'],
                                    file_name = excel_file,
                                    file_url = excels.url(excel_file),
                                    user_id = current_user.id,
                                    valid = passing == 'PASS'
                                   )
            db.session.add(excel_file)
            db.session.commit()
          flash("Excel File {} uploaded".format(excel_file.name))
          return redirect(url_for('excel.display_excel_files'))
    else:
      flash("Error: Problem with adding new Excel File!")

  return render_template('/excel/file_upload.html',form=form, admin=True)

@excel_bp.route("/excel/files",methods=["GET"])
def display_excel_files():
  excel_files = ExcelFiles.query.all()
  return render_template('/excel/display_files.html', excel_files=excel_files)

@excel_bp.route("/excel/delete", methods=['GET'])
def delete_excel_file():
  try:
    file_id = request.args.get('file_id')
    excel_file_obj = ExcelFiles.query.filter(ExcelFiles.id == file_id).first()
    os.remove(os.path.join(current_app.config['UPLOADED_EXCELS_DEST'],excel_file_obj.file_name))

    db.session.query(ExcelFiles).filter_by(id = file_id).delete()
    db.session.commit()

    flash("The Excel file has been successfully deleted")
    return redirect(url_for("excel.display_excel_files"))
  except Exception as e:
    flash('Somthing unexpected happened. This error has been logged: {}'.format(str(e)),'error')
    return redirect(request.referrer)

@excel_bp.route('/excel/download',methods=["GET"])
def download_excel_file():
  try:
    file_id = request.args.get('file_id')
    eF = ExcelFiles.query.filter(ExcelFiles.id==file_id).first()
    if eF is None:
      flash("File {} not available for download".format(file_id))
      redirect(request.referrer)

    return send_from_directory(current_app.config['UPLOADED_EXCELS_DEST'],
                               eF.file_name, as_attachment=True)
  except Exception as e:
    flash("There was an error trying to download the Excel File {}".format(e))
    return redirect(request.referrer)

@excel_bp.route('/excel/deploy',methods=["GET"])
def deploy_excel_file():
  try:
    file_id = request.args.get('file_id')
    eF = ExcelFiles.query.filter(ExcelFiles.id==file_id).first()
    eFP = os.path.join(current_app.config['UPLOADED_EXCELS_DEST'],eF.file_name)
    if eF is None:
      flash("File {} not available for deployment".format(file_id))
      return redirect(request.referrer)
    passing, msgs = validate_headers_from_excel(eFP)
    print("____")
    if passing != "PASS":
      for msg in msgs:
        flash(msg)
      return redirect(request.referrer)

    ## convert
    output_file_name = os.path.join(current_app.config['UPLOADED_EXCELS_DEST'],
                                    "{}_bivizio_conv.csv".format(eF.file_name.rsplit(".")[0]))
    nrc2bivisio(eFP,output_file_name,current_app.config['GOOGLE_MAPS_API_KEY'])
    flash("File Deployed, Message Sent")
    return redirect(url_for('excel.display_excel_files'))
  except Exception as e:
    flash("There was an error trying to download the Excel File {}".format(e))
    return redirect(request.referrer)

