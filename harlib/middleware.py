#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014, Andrew Robbins, All rights reserved.
# 
# This library ("it") is free software; it is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License ("LGPLv3") <https://www.gnu.org/licenses/lgpl.html>.
'''
harlib - HTTP Archive (HAR) format library
'''
from __future__ import absolute_import
import json
import harlib

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
        import json

        d = {'startedDateTime': None,
             'time': 0.0,
             'request': harlib.HarRequest(request),
             'response': harlib.HarResponse(response)}

        s = json.dumps(
            harlib.HarEntry(d).to_json(with_content=False), 
            indent=4)

        print(s)

        return response

    def process_exception(self, request, exception):
        #print('process_exception(%s, %s)' % (type(request), type(exception)))
        #return exception
        pass
