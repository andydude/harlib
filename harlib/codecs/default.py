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
import collections
import harlib

class DefaultCodec(object):

    dict_class = dict
    modules = ['__builtin__']

    def __init__(self):
        pass

    ##########################################################################################
    ## Encoding

    def encode(self, har, raw_class):
        assert raw_class.__module__ in self.modules
        method_name = 'encode_%s_to_%s' % (
            har.__class__.__name__, raw_class.__name__)
        return getattr(self, method_name)(har)

    def encode_HarHeader_to_tuple(self, har):
        return (har.name, har.value)

    def encode_HarCookie_to_tuple(self, har):
        return (har.name, har.value)

    ##########################################################################################
    ## Decoding

    def decode(self, raw, har_class):
        assert raw.__class__.__module__ in self.modules
        method_name = 'decode_%s_from_%s' % (
            har_class.__name__, raw.__class__.__name__)
        return getattr(self, method_name)(raw)

    def decode_HarPostDataParam_from_tuple(self, raw):
        har = self.dict_class()
        har['name'] = raw[0]

        obj = raw[1:]

        if len(obj) == 1:
            har['value'] = obj[0]
        elif len(obj) == 2:
            har['value'] = obj[1]
            har['fileName'] = obj[0]
        elif len(obj) == 3:
            har['value'] = obj[1]
            har['fileName'] = obj[0]
            har['contentType'] = obj[2]
        elif len(obj) == 4:
            har['value'] = obj[1]
            har['fileName'] = obj[0]
            har['contentType'] = obj[2]
            if hasattr(obj[3], 'items'):
                har['_headers'] = map(HarHeader, obj[3].items())
        else:
            pass

        return har

    def decode_HarHeader_from_tuple(self, raw):
        har = self.dict_class()
        har['name'] = raw[0]
        har['value'] = raw[1]
        return har

    def decode_HarCookie_from_tuple(self, raw):
        har = self.dict_class()
        har['name'] = raw[0]
        har['value'] = raw[1]
        return har
