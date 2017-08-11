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
from harlib.test_utils import TestUtils
from harlib.objects import (
    HarFile, HarLog, HarEntry,
    HarRequest, HarResponse)
from harlib.compat import OrderedDict
import harlib.api
import six
import json



class ApiTests(TestUtils):

    def setUp(self):
        self.har_file = HarFile([])
        self.har_file_data = OrderedDict([
            ('log', OrderedDict([
                ('version', '1.2'),
                ('creator', OrderedDict([
                    ('name', 'harlib'),
                    ('version', '0')])),
                ('entries', [
                    OrderedDict([
                        ('startedDateTime', '2017-07-28T17:06:22.508Z'),
                        ('time', 0),
                        ('request', OrderedDict([
                            ('method', 'GET'),
                            ('url', '/'),
                            ('cookies', []),
                            ('headers', []),
                            ('queryString', [])])),
                        ('response', OrderedDict([
                            ('status', 200),
                            ('statusText', 'OK'),
                            ('cookies', []),
                            ('headers', []),
                            ('content', {'mimeType': ''})]))])
                ])]))])

    def test_2_api_dump(self):
        writer = six.StringIO()
        harlib.api.dump(self.har_file, writer)
        s = writer.getvalue()
        self.assertTrue(isinstance(s, six.text_type))

    def test_3_api_dumps(self):
        s = harlib.api.dumps(self.har_file)
        self.assertTrue(isinstance(s, six.text_type))
        
    def test_4_api_dumpd(self):
        d = harlib.api.dumpd(self.har_file)
        self.assertTrue(isinstance(d, OrderedDict))

    def test_5_api_loadd(self):
        d = self.har_file_data

        obj = harlib.api.loadd(d)
        self.assertTrue(isinstance(obj, HarFile))

        obj = harlib.api.loadd(d['log'])
        self.assertTrue(isinstance(obj, HarLog))

        e = d['log']['entries'][0]

        obj = harlib.api.loadd(e)
        self.assertTrue(isinstance(obj, HarEntry))
                                         
        obj = harlib.api.loadd(e['request'])
        self.assertTrue(isinstance(obj, HarRequest))
                                         
        obj = harlib.api.loadd(e['response'])
        self.assertTrue(isinstance(obj, HarResponse))

        with self.assertRaises(AssertionError):
            obj = harlib.api.loadd(None)
            
        with self.assertRaises(ValueError):
            obj = harlib.api.loadd({})
        
    def test_5_api_loads(self):
        s = json.dumps(self.har_file_data)
        
        obj = harlib.api.loads(s)
        self.assertTrue(isinstance(obj, HarFile))

    def test_6_api_loadf_chrome(self):
        with open('tests/data/chrome.har') as reader:
            d = json.load(reader)

        obj = harlib.api.loadd(d)
        self.assertTrue(isinstance(obj, HarFile))
            
        
    def test_6_api_loadf_firefox(self):
        with open('tests/data/firefox.har') as reader:
            d = json.load(reader)

        obj = harlib.api.loadd(d)
        self.assertTrue(isinstance(obj, HarFile))
