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
from metaobject import MetaObject
import logging
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

logger = logging.getLogger(__name__)

# Superclass for all HAR model objects
class HarObject(MetaObject):

    _ordered = ()

    def __init__(self, obj=None):
        super(HarObject, self).__init__(obj)
        self._ordered = self._ordered or self._required
        self._reserved += ['_ordered', '_codecs']

    def items(self):
        def key(item):
            try: order = self._ordered.index(item[0])
            except ValueError: order = 9999
            return order

        # if we have a specific order, then sort keys
        if hasattr(self, '_ordered') and len(self._ordered) > 0:
            items = self._changed_items()
            items.sort(key=key)
            return items

        # we want to see private attributes as well
        return self._changed_items()

    def to_json(self, dict_class=OrderedDict):
        return super(HarObject, self).to_json(dict_class=dict_class)

    def decode(self, raw):
        mod = raw.__class__.__module__
        for codec in self._codecs:
            if mod in codec.modules:
                har = codec.decode(raw, self.__class__)
                return har
        raise ValueError("%s could not be decoded" % raw.__class__)

    def encode(self, raw_class):
        mod = raw_class.__module__
        for codec in self._codecs:
            if mod in codec.modules:
                raw = codec.encode(self, raw_class)
                return raw
        raise ValueError("%s could not be encoded" % raw_class)

    def serialize(self, io, raw):
        codec = harlib.codecs.requests.RequestsCodec()
        codec.serialize(io, raw, self.__class__)

    def unserialize(self, io):
        raise ValueError("%s could not be unserialized" % raw.__class__)

def initialize_codecs():
    if hasattr(HarObject, '_codecs'):
        return

    HarObject._codecs = []

    try:
        import harlib.codecs.requests
        HarObject._codecs.append(harlib.codecs.requests.Urllib3Codec())
        HarObject._codecs.append(harlib.codecs.requests.RequestsCodec())
    except:
        print("no requests")

    try:
        import harlib.codecs.httplib
        HarObject._codecs.append(harlib.codecs.httplib.Urllib2Codec())
        HarObject._codecs.append(harlib.codecs.httplib.HttplibCodec())
    except:
        print("no httplib")

    try:
        import harlib.codecs.django
        HarObject._codecs.append(harlib.codecs.django.DjangoCodec())
    except:
        print("no django")

    try:
        import harlib.codecs.default
        HarObject._codecs.append(harlib.codecs.default.DefaultCodec())
    except:
        print("no default")

initialize_codecs()
