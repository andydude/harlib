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
import requests
import unittest
import harlib
from harlib.test_utils import TestUtils


class TestRequestsPreparedRequest(TestUtils):

    def setUp(self):
        self.req = requests.Request(
            'POST', 'http://httpbin.org/post',
            data={'username': 'bob', 'password': 'yes'},
            headers={'X-File': 'requests'})
        self.preq = self.req.prepare()

    def test_1_from_requests(self):
        har_req = harlib.HarRequest(self.preq)

        self.assertEqual(har_req.method, self.preq.method)
        self.assertEqual(har_req.url, self.preq.url)
        self.assertEqual(har_req.httpVersion, "HTTP/1.1")
        # self.assertEqual(har_req.get_header("Content-Type"),
        #                  "application/json")
        # self.assertEqual(har_req.postData.mimeType,
        #                  "application/json")

    def test_2_to_requests(self):
        har_preq = harlib.HarRequest(self.preq)
        to_preq = har_preq.encode(requests.PreparedRequest)
        self.assertEqualPreparedRequest(to_preq, self.preq)


class TestRequestsRequest(TestUtils):

    def setUp(self):
        self.req = requests.Request(
            'POST', 'http://httpbin.org/post',
            data={'username': 'bob', 'password': 'yes'},
            headers={'X-File': 'requests'})

    def test_1_from_requests(self):
        req = requests.Request(
            'GET',  'http://httpbin.org/get',
            params={'username': 'bob', 'password': 'yes'})
        har_req = harlib.HarRequest(req)

        self.assertEqual(har_req.method, req.method)
        self.assertEqual(har_req.url, req.url)
        self.assertEqual(har_req.httpVersion, "HTTP/1.1")
        self.assertEqual(har_req.get_param("username"), "bob")
        self.assertEqual(har_req.get_param("password"), "yes")

    def test_2_from_requests(self):
        har_req = harlib.HarRequest(self.req)

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
