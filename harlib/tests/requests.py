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

import json
import requests
import unittest

from .... import utils
from ... import har

class TestRequestsPreparedRequest(unittest.TestCase):

    def setUp(self):
        self.req = requests.Request('POST', 'http://httpbin.org/post',
                                  data={'username': 'bob', 'password': 'yes'},
                                  headers={'X-File': 'requests'})
        self.preq = self.req.prepare()
    def tearDown(self):
        pass

    def test_1_from_requests(self):
        har_req = har.HarRequest(self.preq)
        #print(har_req.dumps())

        self.assertEqual(har_req.method, self.preq.method)
        self.assertEqual(har_req.url, self.preq.url)
        self.assertEqual(har_req.httpVersion, "HTTP/1.1")
        #self.assertEqual(har_req.get_header("Content-Type"), "application/json")
        #self.assertEqual(har_req.postData.mimeType, "application/json")

    def test_2_to_requests(self):
        self.assertTrue(True)

class TestRequestsRequest(unittest.TestCase):

    def setUp(self):
        self.req = requests.Request('POST', 'http://httpbin.org/post',
                                  data={'username': 'bob', 'password': 'yes'},
                                  headers={'X-File': 'requests'})
    def tearDown(self):
        pass

    def test_1_from_requests(self):
        req = requests.Request('GET', 
                               'http://httpbin.org/get',
                               params={'username': 'bob', 'password': 'yes'})
        har_req = har.HarRequest(req)
        #print(har_req.dumps())

        self.assertEqual(har_req.method, req.method)
        self.assertEqual(har_req.url, req.url)
        self.assertEqual(har_req.httpVersion, "HTTP/1.1")
        self.assertEqual(har_req.get_param("username"), "bob")
        self.assertEqual(har_req.get_param("password"), "yes")

    def test_2_from_requests(self):
        har_req = har.HarRequest(self.req)
        #print(har_req.dumps())

        self.assertEqual(har_req.method, self.req.method)
        self.assertEqual(har_req.url, self.req.url)
        self.assertEqual(har_req.httpVersion, "HTTP/1.1")
        self.assertEqual(har_req.get_header("X-File"), "requests")
        self.assertEqual(har_req.post_param("username").value, "bob")
        self.assertEqual(har_req.post_param("password").value, "yes")

    def test_3_to_requests(self):
        self.assertTrue(True)

class TestRequestsResponse(unittest.TestCase):

    def setUp(self):
        self.resp = requests.post('http://httpbin.org/post',
                                  data={'username': 'bob', 'password': 'yes'},
                                  headers={'X-File': 'requests'})
    def tearDown(self):
        pass

    def test_1_from_requests(self):
        har_resp = har.HarResponse(self.resp)
        #print(har_resp.dumps())

        self.assertEqual(har_resp.status, self.resp.status_code)
        self.assertEqual(har_resp.statusText, self.resp.reason)
        self.assertEqual(har_resp.httpVersion, "HTTP/1.1")
        self.assertEqual(har_resp.get_header("Content-Type"), "application/json")
        self.assertEqual(har_resp.content.mimeType, "application/json")
        
        json_resp = json.loads(har_resp.content.text)
        #print(har_resp.content.text)
        self.assertEqual(json_resp["url"], "http://httpbin.org/post")
        self.assertEqual(json_resp["headers"]["Connection"], "close")
        self.assertEqual(json_resp["headers"]["Host"], "httpbin.org")
        self.assertEqual(json_resp["headers"]["X-File"], "requests")
        self.assertEqual(json_resp["headers"]["Content-Type"], 
                         "application/x-www-form-urlencoded")
        self.assertTrue(json_resp["headers"]["User-Agent"]
                        .startswith("python-requests"))

    def test_2_to_requests(self):
        #print(repr(vars(self.resp)))
        har_resp = har.HarEntry(self.resp)
        #print(repr(har_resp))
        to_resp = har_resp.to_requests()
        #print(repr(vars(to_resp)))
        self.assertEqualResponse(to_resp, self.resp)

    def assertEqualHTTPResponse(self, resp, resp2, msg=None):
        ResponseCls = requests.packages.urllib3.HTTPResponse
        self.assertEqual(resp2.__class__, ResponseCls)
        self.assertEqual(resp.__class__, ResponseCls)
        self.assertEqual(resp.status, resp2.status)
        self.assertEqual(resp.reason, resp2.reason)
        self.assertEqual(resp.strict, resp2.strict)
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
        self.assertEqualHTTPResponse(resp.raw, resp2.raw)

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
        self.assertEqual(len(cookies), len(cookies2), msg)
        #if len(headers) != len(headers2): return
        #keys = utils.dict_sortedkeys(headers)
        #keys2 = utils.dict_sortedkeys(headers2)
        #for i in xrange(len(headers)):

    def assertEqualHeaders(self, headers, headers2, msg=None):
        #print("---1")
        #print(headers)
        #print("---2")
        #print(headers2)
        #print("---")
        self.assertEqual(headers.__class__, headers2.__class__, msg)
        self.assertEqual(len(headers), len(headers2), msg)
        if len(headers) != len(headers2): return
        keys = utils.dict_sortedkeys(headers)
        keys2 = utils.dict_sortedkeys(headers2)
        for i in xrange(len(headers)):
            self.assertEqual(keys[i].lower(), keys2[i].lower(), msg)
            self.assertEqual(headers[keys[i]], headers2[keys2[i]], msg)
            self.assertEqual(headers[keys[i]].__class__, headers2[keys2[i]].__class__, msg)

    def assertEqualHistory(self, history, history2, msg=None):
        self.assertEqual(len(history), len(history2), msg)
        if len(history) != len(history2): return
        for i in xrange(len(history)):
            self.assertEqualPreparedRequest(history[i], history2[i], msg)


#class TestRequestsSession(unittest.TestCase):
#
#    def setUp(self):
#        pass
#
#    def tearDown(self):
#        pass
#
#    def testNone(self):
#        self.assertTrue(True)
#
#
#
#    def test_1_from_requests():
#
#    def test_1_to_json
#    def test_1_from_json
#    def test_1_to_urllib3
#    def test_1_from_urllib3
#    def test_1_to_django
#    def test_1_from_django

if __name__ == '__main__':
    unittest.main(verbosity=2)
