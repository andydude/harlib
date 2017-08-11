#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014-2017, Andrew Robbins, All rights reserved.
#
# This library ("it") is free software; it is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; you can redistribute it and/or
# modify it under the terms of LGPLv3 <https://www.gnu.org/licenses/lgpl.html>.

from __future__ import absolute_import
import collections
from .metamodel import HarObject

from .messages import (
    HarCookie,
    HarHeader,
    HarMessageBody,
    HarMessage,
)


class HarResponseBody(HarMessageBody):
    # <content>

    _required = [
        'mimeType',
    ]

    _optional = {
        'size': -1,
        'text': '', 		# HAR-1.2 optional string
        'comment': '',
        'compression': -1, 	# HAR-1.2 optional number
        'encoding': '', 	# HAR-1.2 optional string
    }

    _types = {
        'size': int,
        'compression': int,
    }

    def __init__(self, obj=None):
        har = obj or None

        if isinstance(obj, collections.Mapping):
            har = obj
        elif isinstance(obj, HarObject):
            har = obj.to_json()
        else:
            har = self.decode(obj)

        super(HarResponseBody, self).__init__(har)


class HarResponse(HarMessage):

    _required = [
        'status',
        'statusText',
        'cookies',
        'headers',
        'content',
    ]

    _optional = {
        'httpVersion': '', 	# HAR-1.2 required
        'headersSize': -1,
        'bodySize': -1,
        'redirectURL': '',
        'comment': '',
        '_statusLineSize': -1,
        '_statusLine': '',
        '_checkResult': None,
        '_parseResult': None,
    }

    _types = {
        'status': int,
        'bodySize': int,
        'headersSize': int,
        'cookies': [HarCookie],
        'headers': [HarHeader],
        'content': HarResponseBody,
        '_statusLineSize': int,
    }

    _ordered = [
        'status',
        'statusText',
        'httpVersion',

        'cookies',
        'headers',
        'content',
        'redirectURL',
        'headersSize',
        'bodySize',
        'comment',
        '_statusLine',
        '_statusLineSize',
        '_checkResult',
        '_parseResult',
    ]

    def __init__(self, obj=None):
        har = obj or None

        if isinstance(obj, collections.Mapping):
            har = obj
        elif isinstance(obj, HarObject):
            har = obj.to_json()
        else:
            har = self.decode(obj)

        super(HarResponse, self).__init__(har)
