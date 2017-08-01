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
from harlib.test_utils import TestUtils, HTTPBIN_ORIGIN
from harlib.sessions import HarSession


class SessionTests(TestUtils):

    def setUp(self):
        self.session = HarSession('temp.har')
        
    def test_1_session(self):
        url = '%s/get' % HTTPBIN_ORIGIN
        response = self.session.get(url)
        self.assertTrue(len(self.session._entries) == 1)
