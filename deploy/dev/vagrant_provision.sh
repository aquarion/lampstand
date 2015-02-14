#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

echo '-------------------------------------------------------------------'
echo ">> Debian"
echo '-------------------------------------------------------------------'

echo "> Update... "
apt-get update -qq
echo "> Install... "
# Install all the requirements
cat /vagrant/deploy/requirements.dpkg | xargs apt-get install -qqy

hostname lampstand
echo "127.0.0.1	lampstand" >> /etc/hosts

## Python 

echo '-------------------------------------------------------------------'
echo ">> Installing Python Packages"
echo '-------------------------------------------------------------------'
echo -ne "source /etc/bash_completion.d/virtualenvwrapper; 
    mkvirtualenv -q lampstand --system-site-packages;
	workon lampstand; 
	pip install -qr /vagrant/requirements.pip --log ~/pip.log;
	python -m nltk.downloader all" | su vagrant -c bash

gem install foreman

echo '-------------------------------------------------------------------'
echo ">> Setup MySQL"
echo '-------------------------------------------------------------------'
export PASSWORD=iMPOrTanT
apt-get install -q -y mysql-server-5.5 mysql-client-5.5
mysqladmin -u root password $PASSWORD
echo "create database lampstand;" | mysql -uroot -p$PASSWORD
echo "grant all on lampstand.* to webapp@localhost identified by 'webapp'" | mysql -uroot -p$PASSWORD

cat /vagrant/schema.sql | mysql -uwebapp -pwebapp lampstand
#cat /vagrant/data/example_data.sql | mysql -uwebapp -pwebapp lampstand

su vagrant -c "cp /vagrant/config.dev.ini /vagrant/config.ini "