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
import harlib
import logging

logger = logging.getLogger(__name__)


class HarLoggingMiddleware(object):
    '''
    This is an example of what your django settings.py should look like:

MIDDLEWARE_CLASSES = (
    ...
    'harlib.middleware.HarLoggingMiddleware',
)
    '''

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        try:
            d = {'startedDateTime': None,
                 'time': 0.0,
                 'request': harlib.HarRequest(request),
                 'response': harlib.HarResponse(response)}

            s = json.dumps(harlib.HarEntry(d).to_json(with_content=False))
            logger.info(s)
        except Exception as err:
            logger.error("%s %s" % (type(err), repr(err)))

        return response

    def process_exception(self, request, exception):
        # print('process_exception(%s, %s)' % (type(request), type(exception)))
        # return exception
        pass
