#!/usr/bin/env python
#
# Electrum - lightweight Bitcoin client
# Copyright (C) 2015 THomas Voegtlin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import time, thread, sys, socket, os, re
import urllib2,json
import Queue
import traceback
import plyvel

from electrum import Wallet, Interface, SimpleConfig

import ConfigParser
config = ConfigParser.ConfigParser()
config.read("/etc/cosignerpool.conf")
my_password = config.get('main','password')
my_host = config.get('main','host')
my_port = config.getint('main','port')
dbpath = config.get('main', 'dbpath')


import json, ast
import hmac, base64, struct, hashlib, time
import electrum.bitcoin as bitcoin
import electrum.transaction as transaction
import electrum

electrum.util.set_verbosity(1)

requests = {}


def run_server():
    from SimpleXMLRPCServer import SimpleXMLRPCServer
    server = SimpleXMLRPCServer((my_host, my_port), allow_none=True, logRequests=True)
    server.register_function(delete, 'delete')
    server.register_function(get, 'get')
    server.register_function(put, 'put')
    server.register_function(dump, 'dump')
    server.register_function(lambda: setattr(server,'running', False), 'stop')
    server.running = True
    while server.running:
        server.handle_request()

def get(key):
    o = db.get(key)
    return o

def put(key, value):
    print key, value
    db.put(key, value)

def delete(key):
    db.delete(key)

def dump():
    out = {}
    for key, value in db:
        out[ key ]= value
    return out

def handle_command(cmd):
    import xmlrpclib
    server = xmlrpclib.ServerProxy('http://%s:%d'%(my_host, my_port), allow_none=True)

    try:
        if cmd == 'stop':
            out = server.stop()
        else:
            out = "unknown command"
    except socket.error:
        print "Server not running"
        return 1

    print out
    return 0

if __name__ == '__main__':

    if len(sys.argv) > 1:
        ret = handle_command(sys.argv[1])
        sys.exit(ret)

    db = plyvel.DB(dbpath, create_if_missing=True, compression=None)
    run_server()
    db.close()


