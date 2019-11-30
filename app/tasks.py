from app import create_app
from rq import get_current_job
from app import db
from app.models import Task, User,ExcelFiles
from app.excel.bivisio_api_client import Bivzio_API_Client
import sys
import os
import time
import json

app = create_app()
app.app_context().push()

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.users.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        db.session.commit()

def update_bivisio_database_task(user_id,eF):
    try:
        user = User.query.get(user_id)
        _set_task_progress(0)
        b_api_client = Bivzio_API_Client(_token=app.config['BIVISIO_API_KEY'],
                                         _url=app.config['BIVISIO_API_URL'])
        #json_array = b_api_client.convert_nrc_workbook_to_biv_json_list(eF)
        json_array = json.loads(eF.contents)
        total_entries = len(json_array)

        count=0
        for biv_json in json_array:
            b_api_client.update_bivisio_entry(biv_json)
            #with open('/tmp/file.txt','a') as f:
            #    f.write("{}\n".format(biv_json))
            count += 1
            _set_task_progress(100 * count // total_entries)
        eFH = ExcelFiles.query.filter(ExcelFiles.id==eF.id).first()
        eFH.set_deployed()
    except:
        print("setting Error")
        _set_task_progress("Error")
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
