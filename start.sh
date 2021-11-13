#!/bin/bash
/usr/local/bin/gunicorn -t 500 -k sync -w 3 -b 0.0.0.0:5000 --access-logfile - --access-logformat  "%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" %({http_accept}e)s %({accept}i)s"  uwsgi:app &
python /srv/transformer_frontend/app/preproc_server.py -s aligner_encs -p 9010 &
wait
#python preproc_server.py -s aligner_encs -p 9011
