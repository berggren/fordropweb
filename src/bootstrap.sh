#!/bin/sh

if [ ! -d db ]; then
	mkdir db
fi

if [ ! -d storage ]; then
	mkdir -p storage/files
fi
