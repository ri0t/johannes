#!/bin/sh

JO=/home/c-lib/src/johannes
. $JO/venv/bin/activate

python $JO/server.py &
