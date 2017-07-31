#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014-2017, Andrew Robbins, All rights reserved.
#
# This library ("it") is free software; it is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; you can redistribute it and/or
# modify it under the terms of LGPLv3 <https://www.gnu.org/licenses/lgpl.html>.
'''
harlib - HTTP Archive (HAR) format library
'''
from __future__ import absolute_import

import harlib
import json
import unittest

from six.moves import http_client
from harlib.test_utils import TestUtils, HTTPBIN_ORIGIN


class TestHttplibHTTPResponse(TestUtils):

    timeout = None

    def setUp(self):
        ConnectionCls = http_client.HTTPConnection
        host = HTTPBIN_ORIGIN.split('/')[-1]
        # self.sock = self.Socket((host, 80), self.timeout)
        self.conn = ConnectionCls(host)

    def tearDown(self):
        self.conn.close()
        # self.sock.close()

    def test_1_from_httplib(self):
        self.conn.request("GET", "/get")
        resp = self.conn.getresponse()

        har_resp = harlib.HarResponse(resp)
        self.assertEqual(har_resp.status, 200)
        self.assertEqual(har_resp.statusText, "OK")
        self.assertEqual(har_resp.httpVersion, "HTTP/1.1")
        self.assertEqual(har_resp.get_header("Content-Type"),
                         "application/json")
        self.assertEqual(har_resp.content.mimeType,
                         "application/json")

        json_resp = json.loads(har_resp.content.text)

        host = HTTPBIN_ORIGIN.split('/')[-1]
        self.assertEqual(json_resp["url"], "%s/get" % HTTPBIN_ORIGIN)
        self.assertEqual(json_resp["headers"]["Accept-Encoding"], "identity")
        self.assertEqual(json_resp["headers"]["Host"], host)
        # self.assertEqual(json_resp["headers"]["Connection"], "close")
        # self.assertEqual(har_resp.cookies, [])
        # self.assertEqual(har_resp.redirectURL, "")
        # self.assertEqual(har_resp.headersSize, -1)
        # self.assertEqual(har_resp.bodySize, 0)
        # self.assertEqual(har_resp.comment, "")

    def test_2_to_httplib(self):
        self.conn.request("GET", "/get")
        resp = self.conn.getresponse()
        har_resp = harlib.HarEntry(resp)
        to_resp = har_resp.encode(http_client.HTTPResponse)
        self.assertEqualHttplibHTTPResponse(to_resp, resp)

    def test_3_mess_up_httplib(self):
        self.conn.request("GET", "/get")
        resp = self.conn.getresponse()

        # Mess stuff up so it is different than default
        resp.debuglevel = 3
        resp.strict = 1
        resp.version = 9
        resp.status = 418
        resp.reason = "I'm a teapot"

        har_resp = harlib.HarEntry(resp)

        to_resp = har_resp.encode(http_client.HTTPResponse)
        self.assertEqualHttplibHTTPResponse(to_resp, resp)


# class TestHttplibHTTPConnection(unittest.TestCase):
#
#    Socket = staticmethod(socket.create_connection)
#    Connection = staticmethod(httplib.HTTPConnection)
#    timeout = socket._GLOBAL_DEFAULT_TIMEOUT
#
#    def setUp(self):
#        host = HTTPBIN_ORIGIN.split('/')[-1]
#        #self.sock = self.Socket((host, 80), self.timeout)
#        self.conn = self.Connection(host)
#
#    def tearDown(self):
#        self.conn.close()
#        #self.sock.close()
#
#    def test_1_from_httplib(self):
#        self.conn.request("GET", "/get")
#        resp = self.conn.getresponse()
#        har_resp = harlib.HarResponse(resp)
#
#    def test_2_to_httplib(self):
#        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
