#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014, Andrew Robbins, All rights reserved.
# 
# This library ("it") is free software; it is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License ("LGPLv3") <https://www.gnu.org/licenses/lgpl.html>.
'''
harlib - HTTP Archive (HAR) format library
'''
from __future__ import absolute_import
import httplib
import json
import socket
import unittest

from ... import har

class TestHttplibHTTPResponse(unittest.TestCase):

    Socket = staticmethod(socket.create_connection)
    Connection = staticmethod(httplib.HTTPConnection)
    timeout = None

    def setUp(self):
        #self.sock = self.Socket(("httpbin.org", 80), self.timeout)
        self.conn = self.Connection("httpbin.org")

    def tearDown(self):
        self.conn.close()
        #self.sock.close()

    def test_1_from_httplib(self):
        self.conn.request("GET", "/get")
        resp = self.conn.getresponse()

        har_resp = har.HarResponse(resp)
        self.assertEqual(har_resp.status, 200)
        self.assertEqual(har_resp.statusText, "OK")
        self.assertEqual(har_resp.httpVersion, "HTTP/1.1")
        self.assertEqual(har_resp.get_header("Content-Type"), "application/json")
        self.assertEqual(har_resp.content.mimeType, "application/json")
        
        json_resp = json.loads(har_resp.content.text)
        self.assertEqual(json_resp["url"], "http://httpbin.org/get")
        self.assertEqual(json_resp["headers"]["Accept-Encoding"], "identity")
        self.assertEqual(json_resp["headers"]["Connection"], "close")
        self.assertEqual(json_resp["headers"]["Host"], "httpbin.org")

        #self.assertEqual(har_resp.cookies, [])
        #self.assertEqual(har_resp.redirectURL, "")
        #self.assertEqual(har_resp.headersSize, -1)
        #self.assertEqual(har_resp.bodySize, 0)
        #self.assertEqual(har_resp.comment, "")

    def test_2_to_httplib(self):
        self.conn.request("GET", "/get")
        resp = self.conn.getresponse()

        har_resp = har.HarEntry(resp)

        to_resp = har_resp.to_httplib()
        self.assertEqual(to_resp.__class__, httplib.HTTPResponse)
        self.assertEqual(to_resp.debuglevel, resp.debuglevel)
        self.assertEqual(to_resp.strict, resp.strict)
        self.assertEqual(to_resp._method, resp._method)
        self.assertEqual(to_resp.version, resp.version)
        self.assertEqual(to_resp.status, resp.status)
        self.assertEqual(to_resp.reason, resp.reason)
        self.assertEqual(to_resp.chunked, resp.chunked)
        self.assertEqual(to_resp.chunk_left, resp.chunk_left)
        self.assertEqual(to_resp.length, resp.length)
        self.assertEqual(to_resp.will_close, resp.will_close)
        #self.assertEqual(to_resp.fp, resp.fp) -- impossible

    def test_3_mess_up_httplib(self):
        self.conn.request("GET", "/get")
        resp = self.conn.getresponse()

        # Mess stuff up so it is different than default
        resp.debuglevel = 3
        resp.strict = 1
        resp.version = 9
        resp.status = 418
        resp.reason = "I'm a teapot"

        har_resp = har.HarEntry(resp)

        to_resp = har_resp.to_httplib()
        self.assertEqual(to_resp.__class__, httplib.HTTPResponse)
        self.assertEqual(to_resp.debuglevel, resp.debuglevel)
        self.assertEqual(to_resp.strict, resp.strict)
        self.assertEqual(to_resp._method, resp._method)
        self.assertEqual(to_resp.version, resp.version)
        self.assertEqual(to_resp.status, resp.status)
        self.assertEqual(to_resp.reason, resp.reason)
        self.assertEqual(to_resp.chunked, resp.chunked)
        self.assertEqual(to_resp.chunk_left, resp.chunk_left)
        self.assertEqual(to_resp.length, resp.length)
        self.assertEqual(to_resp.will_close, resp.will_close)
        #self.assertEqual(to_resp.fp, resp.fp) -- impossible


#class TestHttplibHTTPConnection(unittest.TestCase):
#
#    Socket = staticmethod(socket.create_connection)
#    Connection = staticmethod(httplib.HTTPConnection)
#    timeout = socket._GLOBAL_DEFAULT_TIMEOUT
#
#    def setUp(self):
#        #self.sock = self.Socket(("httpbin.org", 80), self.timeout)
#        self.conn = self.Connection("httpbin.org")
#
#    def tearDown(self):
#        self.conn.close()
#        #self.sock.close()
#
#    def test_1_from_httplib(self):
#        self.conn.request("GET", "/get")
#        resp = self.conn.getresponse()
#        har_resp = har.HarResponse(resp)
#
#    def test_2_to_httplib(self):
#        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
