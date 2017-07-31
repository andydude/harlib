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
from collections import Mapping
from .metamodel import HarObject
from .messages import (
    HarCookie,
    HarHeader,
    HarQueryStringParam,
    HarPostDataParam,
    HarMessageBody,
    HarMessage,
)

try:
    from typing import Any, Dict, List, NamedTuple, Optional
except ImportError:
    pass


class HarRequestBody(HarMessageBody):
    # <postData>

    _required = [
        'mimeType',
    ]

    _optional = {
        '_size': -1,
        'text': '',  # HAR-1.2 required
        'comment': '',
        '_compression': -1,
        '_encoding': '',
        'params': [],
    }

    _types = {
        '_size': int,
        '_compression': int,
        'params': [HarPostDataParam],
    }

    def __init__(self, obj=None):
        # type: (Dict) -> None
        har = obj or None

        if isinstance(obj, Mapping):
            har = obj
        elif isinstance(obj, HarObject):
            har = obj.to_json()
        else:
            har = self.decode(obj)

        super(HarRequestBody, self).__init__(har)


class HarRequest(HarMessage):
    # type: NamedTuple('HarRequest', [
    #     ('method', str),
    #     ('url', str),
    #     ('cookies', List[HarCookie]),
    #     ('headers', List[HarHeader]),
    #     ('queryString', List[HarQueryStringParam]),
    #     ('httpVersion', str),
    #     ('headersSize', int),
    #     ('bodySize', int),
    #     ('postData', HarRequestBody),
    #     ('_requestLine', str),
    #     ('_requestLineSize', str),
    #     ('_endpointID', str),
    #     ('_originURL', str),
    #     ('_required', List[str]),
    #     ('_optional', Dict[str, Any]),
    #     ('_types', Dict[str, Any]),
    #     ('_ordered', List[str]),
    # ])
    
    _required = [
        'method',
        'url',
        'cookies',
        'headers',
        'queryString', 		# HAR-1.2 required
    ]

    _optional = {
        'httpVersion': '', 	# HAR-1.2 required
        'headersSize': -1,
        'bodySize': -1,
        'postData': {'mimeType': 'UNKNOWN'},
        'comment': '',
        '_requestLine': '',
        '_requestLineSize': -1,
        '_endpointID': '',
        '_originURL': '',
    }

    _types = {
        'cookies': [HarCookie],
        'headers': [HarHeader],
        'postData': HarRequestBody,
        'queryString': [HarQueryStringParam],
        'headersSize': int,
        'bodySize': int,
        '_requestLineSize': int,
    }

    _ordered = [
        'method',
        'url',
        'httpVersion',

        'cookies',
        'headers',
        'queryString',
        'postData',
        'headersSize',
        'bodySize',
        'comment',
        '_requestLine',
        '_requestLineSize',
    ]

    def __init__(self, obj=None):
        # type: (Dict) -> None
        har = obj or None

        if isinstance(obj, Mapping):
            har = obj
        elif isinstance(obj, HarObject):
            har = obj.to_json()
        else:
            har = self.decode(obj)

        super(HarRequest, self).__init__(har)

    @property
    def size(self):
        # type: () -> int
        return self.headersSize + self.bodySize

    def get_param(self, name, default=None):
        # type: (str, str) -> Optional[str]
        for param in self.queryString:
            if param.name == name:
                return param.value
        return default

    def post_param(self, name, default=None):
        # type: (str, str) -> Optional[str]
        for param in self.postData.params:
            if param.name == name:
                return param
        return default
