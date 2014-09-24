#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Hackerfleet Technology Demonstrator
# =====================================================================
# Copyright (C) 2011-2014 riot <riot@hackerfleet.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import time
import sys


debug = 10
info = 20
warn = 30
error = 40
critical = 50
off = 100

lvldata = {10: 'DEBUG',
           20: 'INFO',
           30: 'WARN',
           40: 'ERROR',
           50: 'CRITICAL'
}

count = 0

logfile = "/var/log/hfos/service.log"
verbosity = {'global': debug,
             'file': off,
             'console': debug}

start = time.time()


def log(*what, **kwargs):
    if 'lvl' in kwargs:
        lvl = kwargs['lvl']
        if lvl < verbosity['global']:
            return
    else:
        lvl = info

    global count
    global start
    count += 1

    now = time.time() - start
    msg = "[%s] : %5s : %.5f : %5i :" % (time.asctime(),
                                         lvldata[lvl],
                                         now,
                                         count)

    for thing in what:
        msg += " "
        msg += str(thing)

    if lvl >= verbosity['file']:
        try:
            f = open(logfile, "a")
            f.write(msg)
            f.flush()
            f.close()
        except IOError:
            print("Can't open logfile for writing!")
            sys.exit(23)

    if lvl >= verbosity['console']:
        print(str(msg))


