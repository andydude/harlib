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
from __future__ import print_function
from botocore.awsrequest import (
    AWSRequest, AWSPreparedRequest)
# from botocore.vendored.requests.sessions import Session
# from botocore.vendored import requests
# from botocore.vendored.requests.models import (
#    PreparedRequest, Request, Response)
from harlib.objects import HarRequest
from harlib.test_utils import TestUtils


class AWSRequestTests(TestUtils):

    def setUp(self):
        self.request = AWSRequest(url='http://example.com')
        self.prepared_request = AWSPreparedRequest(self.request)
        self.har_request = HarRequest({
            'url': 'http://example.com',
            'method': 'GET',
            'cookies': {},
            'headers': {},
            'queryString': [],
            'postData': {'mimeType': ''},
        })

    def test_1_from_aws_request(self):
        har = HarRequest(self.request)
        self.assertEqual(har.url, self.request.url)

    def test_2_from_aws_prepared_request(self):
        har = HarRequest(self.prepared_request)
        self.assertEqual(har.url, self.prepared_request.url)

    def test_3_to_aws_request(self):
        request = self.har_request.encode(AWSRequest)
        self.assertEqual(request.url, self.request.url)

    def test_4_to_aws_prepared_request(self):
        prepared_request = self.har_request.encode(AWSPreparedRequest)
        self.assertEqual(
            prepared_request.url,
            self.prepared_request.url)
