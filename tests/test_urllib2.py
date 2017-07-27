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
from __future__ import unicode_literals

import json
import unittest
import harlib
import six
from six.moves import http_client
from six.moves import urllib
from harlib.test_utils import TestUtils


class TestUrllib2OpenerDirector(TestUtils):
    Opener = staticmethod(urllib.request.OpenerDirector)

    def setUp(self):
        self.req = self.Connection('httpbin.org')

    def tearDown(self):
        pass


class TestUrllib2Request(TestUtils):
    Request = staticmethod(urllib.request.Request)

    def setUp(self):
        self.req = self.Request(
            'http://httpbin.org/post',
            data='username=bob&password=yes',
            headers={'Accept': '*/*', 'Content-Type':
                     'application/x-www-form-urlencoded'})

    def test_1_from_urllib2(self):

        har_req = harlib.HarRequest(self.req)
        self.assertEqual(har_req.method, 'POST')
        self.assertEqual(har_req.url, 'http://httpbin.org/post')
        self.assertEqual(har_req.httpVersion, 'HTTP/1.1')
        self.assertEqual(har_req.get_header('Accept'), '*/*')
        self.assertEqual(har_req.get_header('Content-Type'),
                         'application/x-www-form-urlencoded')

        self.assertEqual(har_req.postData.params[0].name, 'username')
        self.assertEqual(har_req.postData.params[0].value, 'bob')
        self.assertEqual(har_req.postData.params[1].name, 'password')
        self.assertEqual(har_req.postData.params[1].value, 'yes')

    def test_2_to_urllib2(self):
        har_req = harlib.HarRequest(self.req)
        to_req = har_req.encode(urllib.request.Request)
        self.assertEqualUrllib2Request(to_req, self.req)


class TestUrllib2Response(TestUtils):
    '''
    urllib2 does not have a proper response class
    urllib has a response class called `addinfourl` with:
      .code
      .url
      .headers
      .read()
      .close()
    but there does not seem to be a valid use case for this,
    so it is safe to say it will never be used.
    '''
    Request = staticmethod(urllib.request.Request)

    def setUp(self):
        self.req = self.Request('http://httpbin.org/post',
                                data=b'username=bob&password=yes',
                                headers={'Accept': '*/*', 'Content-Type':
                                         'application/x-www-form-urlencoded'})

    def test_1_from_urllib2(self):
        resp = urllib.request.urlopen(self.req)

        self.assertTrue(isinstance(resp,
                                   (urllib.response.addinfourl,  # PY2
                                    http_client.HTTPResponse)),  # PY3
                        type(resp))

        har_resp = harlib.HarResponse(resp)
        self.assertEqual(har_resp.status, 200)
        self.assertEqual(har_resp.statusText, 'OK')
        self.assertEqual(har_resp.httpVersion, 'HTTP/1.1')
        self.assertEqual(har_resp.get_header('Content-Type'),
                         'application/json')

        json_resp = json.loads(har_resp.content.text)
        self.assertEqual(json_resp['url'], 'http://httpbin.org/post')
        self.assertEqual(json_resp['headers']['Accept'], '*/*')
        self.assertEqual(json_resp['headers']['Accept-Encoding'], 'identity')
        # self.assertEqual(json_resp['headers']['Connection'], 'close')
        self.assertEqual(json_resp['headers']['Host'], 'httpbin.org')
        if six.PY3:
            self.assertEqual(json_resp['headers']['User-Agent'],
                             'Python-urllib/3.6')
        else:
            self.assertEqual(json_resp['headers']['User-Agent'],
                             'Python-urllib/2.7')
        self.assertEqual(json_resp['headers']['Content-Type'],
                         'application/x-www-form-urlencoded')


if __name__ == '__main__':
    unittest.main(verbosity=2)
