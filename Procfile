web: flask db upgrade; flask seed_db; gunicorn nrcmap:app
worker: rq worker -u $REDIS_URL nrc-tasks
