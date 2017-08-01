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
from harlib.objects import HarPage, HarPageTimings


class PageTests(TestUtils):

    def test_1_page(self):
        page_timings = HarPageTimings({})
        page = HarPage({
            'startedDateTime': '2017-07-31T21:04:08.993170Z',
            'id': 'default',
            'title': '',
            'pageTimings': None,
        })
