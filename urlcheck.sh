#!/bin/bash

cd `dirname $0`

#source ./venv/bin/activate
source /home/aquarion/.virtualenvs/lampstand/bin/activate
python ./urlcheck.py # >> lampstand.stdout.log 2>> lampstand.stderr.log &
