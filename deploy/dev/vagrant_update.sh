#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

echo ">> Debian updates"
echo '-------------------------------------------------------------------'
apt-get update -qq
# Install all the requirements
cat /vagrant/deploy/requirements.dpkg | xargs apt-get install -qqy

## Python 
echo '-------------------------------------------------------------------'
echo ">> Python updates"
echo '-------------------------------------------------------------------'

echo -ne "source /etc/bash_completion.d/virtualenvwrapper; 
    mkvirtualenv -q lampstand;
	workon lampstand; 
	pip install -qr /vagrant/requirements.pip --log ~/pip.log" | su vagrant -c bash


echo '-------------------------------------------------------------------'

# echo "To start the web server, run this:"
# echo vagrant ssh -c /vagrant/bin/start_server.sh
# echo "  "
# echo "To run the test matrix (recommended), try this:"
# echo vagrant ssh -c /vagrant/tests/run_tests.sh
# echo "  "
echo "If it's broken, bother Aquarion until it isn't anymore <nicholas@aquarionics.com>"
