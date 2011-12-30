#!/bin/sh

if [ ! -d db ]; then
	mkdir db
fi

if [ ! -d storage ]; then
	mkdir -p storage/files
fi

echo "Now you need to:"
echo "* Edit settings.py"
echo "* Run python manage.py syncdb"
echo ""
