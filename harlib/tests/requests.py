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
import harlib

try:
    import urllib3
except:
    from requests.packages import urllib3

from .utils import TestUtils

class TestRequestsPreparedRequest(TestUtils):

    def setUp(self):
        self.req = requests.Request('POST', 'http://httpbin.org/post',
                                  data={'username': 'bob', 'password': 'yes'},
                                  headers={'X-File': 'requests'})
        self.preq = self.req.prepare()
    def tearDown(self):
        pass

    def test_1_from_requests(self):
        har_req = harlib.HarRequest(self.preq)
        #print(har_req.dumps())

        self.assertEqual(har_req.method, self.preq.method)
        self.assertEqual(har_req.url, self.preq.url)
        self.assertEqual(har_req.httpVersion, "HTTP/1.1")
        #self.assertEqual(har_req.get_header("Content-Type"), "application/json")
        #self.assertEqual(har_req.postData.mimeType, "application/json")

    def test_2_to_requests(self):
        har_preq = harlib.HarRequest(self.preq)
        to_preq = har_preq.encode(requests.PreparedRequest)
        self.assertEqualPreparedRequest(to_preq, self.preq)

class TestRequestsRequest(TestUtils):

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
        har_req = harlib.HarRequest(req)
        #print(har_req.dumps())

        self.assertEqual(har_req.method, req.method)
        self.assertEqual(har_req.url, req.url)
        self.assertEqual(har_req.httpVersion, "HTTP/1.1")
        self.assertEqual(har_req.get_param("username"), "bob")
        self.assertEqual(har_req.get_param("password"), "yes")

    def test_2_from_requests(self):
        har_req = harlib.HarRequest(self.req)
        #print(har_req.dumps())

        self.assertEqual(har_req.method, self.req.method)
        self.assertEqual(har_req.url, self.req.url)
        self.assertEqual(har_req.httpVersion, "HTTP/1.1")
        self.assertEqual(har_req.get_header("X-File"), "requests")
        self.assertEqual(har_req.post_param("username").value, "bob")
        self.assertEqual(har_req.post_param("password").value, "yes")

    def test_3_to_requests(self):
        har_req = harlib.HarRequest(self.req)
        to_req = har_req.encode(requests.Request)
        self.assertEqualRequest(to_req, self.req)

class TestRequestsResponse(TestUtils):

    def setUp(self):
        self.resp = requests.post('http://httpbin.org/post',
                                  data={'username': 'bob', 'password': 'yes'},
                                  headers={'X-File': 'requests'})
    def tearDown(self):
        pass

    def test_1_from_requests(self):
        har_resp = harlib.HarResponse(self.resp)
        #print(har_resp.dumps())

        self.assertEqual(har_resp.status, self.resp.status_code)
        self.assertEqual(har_resp.statusText, self.resp.reason)
        self.assertEqual(har_resp.httpVersion, "HTTP/1.1")
        self.assertEqual(har_resp.get_header("Content-Type"), "application/json")
        self.assertEqual(har_resp.content.mimeType, "application/json")
        
        json_resp = json.loads(har_resp.content.text)
        #print(har_resp.content.text)
        #self.assertEqual(json_resp["headers"]["Connection"], "close")
        self.assertEqual(json_resp["url"], "http://httpbin.org/post")
        self.assertEqual(json_resp["headers"]["Host"], "httpbin.org")
        self.assertEqual(json_resp["headers"]["X-File"], "requests")
        self.assertEqual(json_resp["headers"]["Content-Type"], 
                         "application/x-www-form-urlencoded")
        self.assertTrue(json_resp["headers"]["User-Agent"]
                        .startswith("python-requests"))

    def test_2_to_requests(self):
        har_resp = harlib.HarEntry(self.resp)
        to_resp = har_resp.encode(requests.Response)
        self.assertEqualResponse(to_resp, self.resp)


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
