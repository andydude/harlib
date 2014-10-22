#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014, Andrew Robbins, All rights reserved.
# 
# This library ("it") is free software; it is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License ("LGPLv3") <https://www.gnu.org/licenses/lgpl.html>.
from __future__ import absolute_import
from six.moves import (http_client, urllib)
import collections
import json
import six

from .metamodel import HarObject

from .messages import (
    HarCookie,
    HarHeader,
    HarMessageBody,
    HarMessage,
)

class HarResponseBody(HarMessageBody): # <content>

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

    @property
    def size(self):
        return self.headersSize + self.bodySize

    #def get_body(self, obj):
    #    har = dict()
    #    text = ''
    #
    #    if isinstance(obj, HarObject):
    #        har = obj.toJSON()
    #
    #    if isinstance(obj, django.http.response.HttpResponse):
    #        har['mimeType'] = obj._headers.get('content-type')[1]
    #        text = obj.content
    #
    #    if isinstance(obj, http_client.HTTPResponse):
    #        har['mimeType'] = obj.msg.getheader('content-type')
    #        text = obj.read()
    #
    #    if isinstance(obj, requests.Response):
    #        har['mimeType'] = obj.headers.get('content-type')
    #        try:
    #            text = obj.text
    #        except:
    #            text = ''
    #
    #    har['text'] = text
    #    har['size'] = len(text)
    #    har['compression'] = -1
    #
    #    use_base64 = False
    #    if use_base64:
    #        har['encoding'] = 'base64'
    #        #har['text'] = re-encode
    #
    #    return har

    #def to_httplib(self):
    #    return self.encode(http_client.HTTPResponse)
    #
    #def to_urllib(self):
    #    return self.encode(urllib.response.addinfourl)
    #
    #def to_urllib3(self):
    #    return self.encode(urllib3r.HTTPResponse)
    #
    #def to_requests(self):
    #    return self.encode(requests.Response)
