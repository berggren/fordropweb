fordrop – Forensic Dropbox
----------------

Building the federated social CERT
Information sharing has proven both important and difficult in the field of
computer forensic analysis. The ability to identify occurrences of electronic
evidence across organization boundaries and making this information accessible
and searchable for a larger community is one of the challenges fordrop is trying to
address. By building a social platform where decentralization, federation and
crowd sourcing are central pieces, fordrop makes it easy and safe to share this
information with your fellow investigators. Fordrop enables crowd-sourcing for IT-
forensics.


Installation
------------

These are the raw steps that is required to install all the dependencies.  
Better documentation is on it's way!

apt-get install build-essential  
apt-get install python-dev  
apt-get install libjpeg62-dev  
apt-get install unzip  
apt-get install openjdk-6-jdk  
apt-get install nginx  
easy_install pip  
pip install virtualenv  
mkdir /opt/virtenvs && cd /opt/virtenvs  
virtualenv fordrop  
source /opt/virtenvs/fordrop/bin/activate  
cd /tmp  
wget http://downloads.sourceforge.net/project/jpype/JPype/0.5.4/JPype-0.5.4.2.zip  
unzip JPype-0.5.4.2.zip   
pip install JPype-0.5.4.2/  
pip install -r /opt/fordrop-web/requirements/fordrop.pip  
pip install gunicorn  
pip install PIL  
mkdir /etc/nginx/ssl && cd /etc/nginx/ssl  
openssl genrsa -des3 -out server.key 1024  
openssl rsa -in server.key -out server.key.insecure  
mv server.key.insecure server.key  
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt  
cp /opt/fordrop-web/contrib/fordrop-web.upstart /etc/init/fordrop-web.conf  
cp /opt/fordrop-web/contrib/fordrop-web.nginx /etc/nginx/sites-availible/fordrop-web  
ln -s /etc/nginx/sites-availible/fordrop-web /etc/nginx/sites-enabled/fordrop-web  
service fordrop-web start  
/etc/init.d/nginx restart  