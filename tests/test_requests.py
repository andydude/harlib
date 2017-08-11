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
import unittest
import harlib
from harlib.test_utils import TestUtils, EXAMPLE_ORIGIN, HTTPBIN_ORIGIN
from harlib.objects import HarEntry
from harlib.compat import requests
from harlib.compat import Request
from harlib.compat import RequestException


class TestRequestsResponse(TestUtils):

    def setUp(self):
        self.resp = requests.post(
            '%s/post' % HTTPBIN_ORIGIN,
            data={'username': 'bob', 'password': 'yes'},
            headers={'X-File': 'requests'})

    def test_1_from_requests(self):
        har_resp = harlib.HarResponse(self.resp)

        self.assertEqual(har_resp.status, self.resp.status_code)
        self.assertEqual(har_resp.statusText, self.resp.reason)
        self.assertEqual(har_resp.httpVersion, 'HTTP/1.1')
        self.assertEqual(har_resp.get_header('Content-Type'),
                         'application/json')
        self.assertEqual(har_resp.content.mimeType,
                         'application/json')

        json_resp = json.loads(har_resp.content.text)

        host = HTTPBIN_ORIGIN.split('/')[-1]
        # self.assertEqual(json_resp['headers']['Connection'], 'close')
        self.assertEqual(json_resp['url'], '%s/post' % HTTPBIN_ORIGIN)
        self.assertEqual(json_resp['headers']['Host'], host)
        self.assertEqual(json_resp['headers']['X-File'], 'requests')
        self.assertEqual(json_resp['headers']['Content-Type'],
                         'application/x-www-form-urlencoded')
        self.assertTrue(json_resp['headers']['User-Agent']
                        .startswith('python-requests'))

    def test_2_to_requests(self):
        har_resp = harlib.HarEntry(self.resp)
        to_resp = har_resp.encode(requests.Response)
        self.assertEqualResponse(to_resp, self.resp)

    def test_3_from_requests_error(self):

        req = Request(
            method='GET',
            url='%s/get' % EXAMPLE_ORIGIN)

        with self.assertRaises(RequestException):
            requests.request(**vars(req))

    def test_4_from_requests_redirect(self):

        req = Request(
            method='GET',
            url='%s/redirect/2' % HTTPBIN_ORIGIN)

        resp = requests.request(**vars(req))
        har_log = harlib.HarLog(resp)
        self.assertEqual(len(har_log.entries), 3)

        to_resp = har_log.encode(requests.Response)
        self.assertEqualResponse(to_resp, resp)
        
    def test_5_from_requests_entry(self):
        entry = HarEntry(self.resp)
        
        d = entry.to_json()
        self.assertIn('request', d)
        self.assertIn('response', d)
        self.assertIn('text', d['request']['postData'])
        self.assertIn('text', d['response']['content'])
        
        d = entry.to_json(with_content=False)
        self.assertNotIn('text', d['request']['postData'])
        self.assertNotIn('text', d['response']['content'])

    def test_5_to_requests_entry(self):
        entry = HarEntry(self.resp)
        entry2 = HarEntry(entry)
        self.assertEqual(entry, entry2)
                
        HarEntry({
            'time': 0,
            'request': None,
            'response': None})
                
        with self.assertRaises(ValueError):
            HarEntry([])

        with self.assertRaises(ValueError):
            HarEntry('')

            
if __name__ == '__main__':
    unittest.main(verbosity=2)
