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
import six
import json
from harlib.test_utils import TestUtils
from harlib.tool import har_sort


class HarReplayToolTests(TestUtils):

    def test_execute_har_log(self):
        filename = 'tests/data/firefox.har'

        with open(filename) as reader:
            har_data = json.load(reader)

        har_file = harlib.HarFile(har_data)

        session = harlib.sessions.HarSession(filename='/dev/stdout')
        for entry in har_file.log.entries:
            request = entry.request.encode(requests.Request)
            expected_response = entry.encode(requests.Response)
            self.assertTrue(isinstance(expected_response, requests.Response))
            #actual_response = session.request(**vars(request))
            #self.assertEqual(
            #    type(expected_response),
            #    type(actual_response))
        self.assertTrue(True)
