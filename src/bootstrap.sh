#!/bin/sh

if [ ! -d db ]; then
	mkdir db
fi

if [ ! -d storage ]; then
	mkdir -p storage/files
fi

if [ ! -d static/cache ]; then
	mkdir -p static/cache
fi

cp -af settings_example.py settings.py

python ./manage.py syncdb
python ./manage.py migrate
