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
from requests.packages import urllib3 as urllib3r
from six.moves import http_client, urllib
import requests
import six
import unittest
import urllib3

class TestUtils(unittest.TestCase):

    def assertEqualHttplibHTTPResponse(self, resp, resp2, msg=None):
        ResponseCls = http_client.HTTPResponse
        self.assertEqual(resp2.__class__, ResponseCls)
        self.assertEqual(resp.__class__, ResponseCls)
        self.assertEqual(resp.debuglevel, resp2.debuglevel)
        #self.assertEqual(resp.strict, resp2.strict)
        self.assertEqual(resp._method, resp2._method)
        self.assertEqual(resp.version, resp2.version)
        self.assertEqual(resp.status, resp2.status)
        self.assertEqual(resp.reason, resp2.reason)
        self.assertEqual(resp.chunked, resp2.chunked)
        self.assertEqual(resp.chunk_left, resp2.chunk_left)
        self.assertEqual(resp.length, resp2.length)
        self.assertEqual(resp.will_close, resp2.will_close)
        #self.assertEqual(to_resp.fp, resp.fp) -- impossible

    def assertEqualUrllib2Request(self, req, req2, msg=None):
        self.assertEqual(req2.__class__, urllib.request.Request)
        self.assertEqual(req.__class__, urllib.request.Request)
        self.assertEqual(req.get_full_url(), req2.get_full_url())
        self.assertEqual(req.type, req2.type)
        self.assertEqual(req.host, req2.host)
        self.assertEqual(req.port, req2.port)
        self.assertEqual(req.data, req2.data)
        self.assertEqual(req.headers, req2.headers)
        self.assertEqual(req.unverifiable, req2.unverifiable)
        self.assertEqual(req.origin_req_host, req2.origin_req_host)

    def assertEqualUrllib3HTTPResponse(self, resp, resp2, msg=None):
        ResponseCls = (urllib3.HTTPResponse, urllib3r.HTTPResponse)
        self.assertIn(resp2.__class__, ResponseCls)
        self.assertIn(resp.__class__, ResponseCls)
        self.assertEqual(resp.status, resp2.status)
        self.assertEqual(resp.reason, resp2.reason)
        #self.assertEqual(resp.strict, resp2.strict)
        self.assertEqual(resp.decode_content, resp2.decode_content)
        self.assertEqual(resp.version, resp2.version)
        self.assertEqual(resp._body, resp2._body)
        #self.assertEqual(resp._fp_bytes_read, resp2._fp_bytes_read)
        #self.assertEqual(resp._original_response, resp2._original_response)

        self.assertEqualHeaders(resp.headers, resp2.headers)

        #  -- impossible to serialize and/or compare
        #self.assertEqual(resp._fp, resp2._fp)
        #self.assertEqual(resp._connection, resp2._connection)
        #self.assertEqual(resp._pool, resp2._pool)

    def assertEqualResponse(self, resp, resp2, msg=None):
        self.assertEqual(resp2.__class__, requests.Response)
        self.assertEqual(resp.__class__, requests.Response)
        self.assertEqual(resp._content, resp2._content)
        self.assertEqual(resp._content_consumed, resp2._content_consumed)
        self.assertEqual(resp.status_code, resp2.status_code)
        self.assertEqual(resp.reason, resp2.reason)
        self.assertEqual(resp.url, resp2.url)
        self.assertEqual(resp.encoding, resp2.encoding)
        self.assertEqual(resp.elapsed, resp2.elapsed)

        self.assertEqualHeaders(resp.headers, resp2.headers)
        self.assertEqualCookies(resp.cookies, resp2.cookies)
        self.assertEqualHistory(resp.history, resp2.history)
        self.assertEqualUrllib3HTTPResponse(resp.raw, resp2.raw)

    def assertEqualRequest(self, req, req2, msg=None):
        self.assertEqual(req2.__class__, requests.Request)
        self.assertEqual(req.__class__, requests.Request)
        self.assertEqual(req.method, req2.method, msg=None)
        self.assertEqual(req.url, req2.url, msg=None)
        self.assertEqual(req.headers, req2.headers, msg=None)
        self.assertEqual(req.cookies, req2.cookies, msg=None)
        self.assertEqual(req.files, req2.files, msg=None)
        self.assertEqual(req.data, req2.data, msg=None)
        self.assertEqual(req.params, req2.params, msg=None)
        self.assertEqual(req.auth, req2.auth, msg=None)
        self.assertEqual(req.hooks, req2.hooks, msg=None)

    def assertEqualPreparedRequest(self, req, req2, msg=None):
        self.assertEqual(req2.__class__, requests.PreparedRequest)
        self.assertEqual(req.__class__, requests.PreparedRequest)
        self.assertEqual(req.method, req2.method, msg=None)
        self.assertEqual(req.url, req2.url, msg=None)
        self.assertEqual(req.headers, req2.headers, msg=None)
        self.assertEqual(req._cookies, req2._cookies, msg=None)
        self.assertEqual(req.body, req2.body, msg=None)
        self.assertEqual(req.hooks, req2.hooks, msg=None)

    def assertEqualCookies(self, cookies, cookies2, msg=None):
        self.assertEqual(cookies.__class__, cookies2.__class__, msg)
        self.assertEqual(len(cookies), len(cookies2), msg)
        #if len(headers) != len(headers2): return
        #keys = utils.dict_sortedkeys(headers)
        #keys2 = utils.dict_sortedkeys(headers2)
        #for i in six.moves.range(len(headers)):

    def assertEqualHeaders(self, headers, headers2, msg=None):
        self.assertEqual(headers.__class__, headers2.__class__, msg)
        self.assertEqual(len(headers), len(headers2), msg)
        if len(headers) != len(headers2): return
        keys = sorted(headers.keys())
        keys2 = sorted(headers2.keys())
        for i in six.moves.range(len(headers)):
            self.assertEqual(keys[i].lower(), keys2[i].lower(), msg)
            self.assertEqual(headers[keys[i]], headers2[keys2[i]], msg)
            self.assertEqual(headers[keys[i]].__class__, headers2[keys2[i]].__class__, msg)
        #self.assertEqual(headers, headers2)

    def assertEqualHistory(self, history, history2, msg=None):
        self.assertEqual(len(history), len(history2), msg)
        if len(history) != len(history2): return
        for i in six.moves.range(len(history)):
            self.assertEqualPreparedRequest(history[i], history2[i], msg)
