johannes
========

A rather simple library management system. Dedicated to Johannes.


Install
=======

You need mongodb and pymongo (ideally from your distro):

    sudo apt-get install mongodb python-pymongo 

    cd ~/src/johannes
    virtualenv --site-packages venv
    source venv/bin/activate
    pip install -r requirements.txt

You could probably do this without site packages by linking the ones you
need yourself, that is mostly bson and pymongo itself, afaik.


Running
=======

Just activate the venv and run the server:

    source venv/bin/activate
    python server.py

Currently listens on flask's defaults, i.e. port 5000 on 127.0.0.1

Contribution
============

To help out make this thing greater than it is, head over to

    https://github.com/ri0t/johannes
or

    https://github.com/c-base/johannes

if you prefer the c-base fork :)

License
=======

GPLv3 - see the accompanying LICENSE file.

Authors
=======

This madness started off in June 2014.

Heiko 'riot' Weinen <riot@c-base.org>
Brain
