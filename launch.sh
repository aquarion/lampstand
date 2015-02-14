#!/bin/bash

cd `dirname $0`

#source ./venv/bin/activate
source /etc/bash_completion.d/virtualenvwrapper
workon lampstand
python ./lampstand.py # >> lampstand.stdout.log 2>> lampstand.stderr.log &
