#!/bin/sh

if [ ! -d db ]; then
	mkdir db
fi

if [ ! -d storage ]; then
	mkdir -p storage/files
fi

cp -af settings_example.py settings.py

/bin/env python ./manage.py syncdb
/bin/env python ./manage.py migrate
