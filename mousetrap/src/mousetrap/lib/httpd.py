# -*- coding: utf-8 -*-

# MouseTrap
#
# Copyright 2009 Flavio Percoco Premoli
#
# This file is part of mouseTrap.
#
# MouseTrap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v2 as published
# by the Free Software Foundation.
#
# mouseTrap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mouseTrap.  If not, see <http://www.gnu.org/licenses/>.



"""The Server module of mouseTrap."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import mouse
import thread
import BaseHTTPServer

from .. import debug
from .. import environment as env

class _HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Provides support for communicating with mouseTrap via HTTP.

    To test this, run:

      wget --post-data='move:X,Y' localhost:20433

    """

    def log_request(self, code=None, size=None):
        """
        Override to avoid getting a log message on stdout for
        each GET, POST, etc. request
        """
        pass

    def do_GET(self):
        """
        Handles the GET requests

        Arguments:
        - self: The main object pointer.
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><body><p>mouseTrap %s</p></body></html>" % (env.version))

    def do_POST(self):
        """
        Handles the POST requests

        Arguments:
        - self: The main object pointer.
        """
        contentLength = self.headers.getheader('content-length')
        if contentLength:
            contentLength = int(contentLength)
            inputBody = self.rfile.read(contentLength)

            if inputBody.startswith("move:"):
                X, Y = inputBody[5:].split(",")
                debug.info( "mouseTrap.httpd", "Moving mouse to %s,%s" % (X, Y) )
                mouse.move(int(X), int(Y))
                self.send_response(200, 'OK')
        else:
            print( "mal" )

#class _HTTPRequestThread(threading.Thread):
class HttpdServer:
    """Runs a _HTTPRequestHandler in a separate thread."""

    def __init__( self, port ):
        """
        HttpdServer Init Class.

        Arguments:
        - self: The main object pointer.
        - port: The port to use for the server.
        """
        self.httpd     = None
        self.run       = True
        self.port      = port
        self.connected = False

    def start(self):
        """
        Try to start an HTTP server on self.settings.httpPort

        Arguments:
        - self: The main object pointer.
        """

        while not self.connected:
            self.httpd = BaseHTTPServer.HTTPServer(('', self.port),
                                              _HTTPRequestHandler)
            self.connected = True
                #debug.log( debug.MODULES, "Highest")

        if not self.connected:
            print( "problems" )
            return False

        thread.start_new_thread(self.__handler, ())

    def is_running(self):
        """
        Returns True if running

        Arguments:
        - self: The main object pointer.
        """
        return self.connected

    def __handler( self ):
        """
        Http Server main loop. While running will handle new requests.

        Arguments:
        - self: The main object pointer.
        """
        while self.run:
            self.httpd.handle_request()

