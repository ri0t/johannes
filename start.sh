#!/bin/sh

JO=/home/riot/src/johannes
. $JO/venv/bin/activate

python $JO/server.py &
