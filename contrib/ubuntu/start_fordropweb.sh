#!/bin/bash
  set -e
  LOGFILE=/var/log/fordropweb.log
  LOGDIR=$(dirname $LOGFILE)
  NUM_WORKERS=1
  # user/group to run as
  USER=www-data
  GROUP=www-data
  cd /opt/fordropweb/fordropweb
  source /opt/virtual_envs/fordropweb/bin/activate
  test -d $LOGDIR || mkdir -p $LOGDIR
  exec /opt/virtual_envs/fordropweb/bin/gunicorn_django -w $NUM_WORKERS \
    --user=$USER --group=$GROUP --log-level=debug \
    --log-file=$LOGFILE 2>>$LOGFILE