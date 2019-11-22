#!/bin/bash

cd `dirname $0`

source /home/lampstand/.virtualenvs/lampstand/bin/activate
python ./lampstand.py >> lampstand.stdout.log 2>> lampstand.stderr.log &
