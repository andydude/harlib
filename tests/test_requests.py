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
import json
import requests
import unittest
import harlib
from harlib.test_utils import TestUtils


class TestRequestsResponse(TestUtils):

    def setUp(self):
        self.resp = requests.post(
            'http://httpbin.org/post',
            data={'username': 'bob', 'password': 'yes'},
            headers={'X-File': 'requests'})

    def test_1_from_requests(self):
        har_resp = harlib.HarResponse(self.resp)

        self.assertEqual(har_resp.status, self.resp.status_code)
        self.assertEqual(har_resp.statusText, self.resp.reason)
        self.assertEqual(har_resp.httpVersion, "HTTP/1.1")
        self.assertEqual(har_resp.get_header("Content-Type"),
                         "application/json")
        self.assertEqual(har_resp.content.mimeType,
                         "application/json")

        json_resp = json.loads(har_resp.content.text)

        # self.assertEqual(json_resp["headers"]["Connection"], "close")
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
