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
from metaobject import MetaObject
import logging
import harlib.codecs
from harlib.compat import OrderedDict

try:
    from typing import Any, BinaryIO, Dict, List, NamedTuple, Optional, Tuple
except ImportError:
    pass

logger = logging.getLogger(__name__)


class HarObject(MetaObject):
    # type: NamedTuple('HarObject', [
    #     ('comment', str),
    #     ('_required', List[str]),
    #     ('_optional', Dict[str, Any]),
    #     ('_types', Dict[str, Any]),
    #     ('_ordered', List[str]),
    # ])
    '''
    Superclass for all HAR model objects
    '''
    _ordered = ()

    def __init__(self, obj=None):
        # type: (Dict) -> None
        super(HarObject, self).__init__(obj)
        self._ordered = self._ordered or self._required
        self._reserved += ['_ordered', '_codecs']

    def items(self):
        # type: () -> List[Tuple[str, str]]
        def key(item):
            # type: (Tuple[str, str]) -> int
            try:
                order = self._ordered.index(item[0])
            except ValueError:
                order = 9999
            return order

        # if we have a specific order, then sort keys
        if hasattr(self, '_ordered') and len(self._ordered) > 0:
            items = self._changed_items()
            items.sort(key=key)
            return items

        # we want to see private attributes as well
        return self._changed_items()

    def to_json(self, dict_class=OrderedDict, with_content=True):
        # type: (type, bool) -> Dict
        return super(HarObject, self).to_json(dict_class=dict_class)

    def decode(self, raw):
        # type: (Any) -> HarObject
        mod = raw.__class__.__module__
        for codec in self._codecs:
            if mod in codec.modules:
                har = codec.decode(raw, self.__class__)
                return har
        raise ValueError("%s could not be decoded" % raw.__class__)

    def encode(self, raw_class):
        # type: (type) -> Any
        mod = raw_class.__module__
        for codec in self._codecs:
            if mod in codec.modules:
                raw = codec.encode(self, raw_class)
                return raw
        raise ValueError("%s could not be encoded" % raw_class)

    def serialize(self, io, raw):
        # type: (BinaryIO, Any) -> None
        from harlib.codecs.requests import RequestsCodec
        codec = RequestsCodec()
        codec.serialize(io, raw, self.__class__)

    def unserialize(self, io):
        # type: (BinaryIO) -> None
        raise ValueError("%s could not be unserialized" % io.__class__)


def initialize_codecs():
    # type: () -> None
    if hasattr(HarObject, '_codecs'):
        return

    HarObject._codecs = []

    try:
        import harlib.codecs.requests
        HarObject._codecs.append(harlib.codecs.requests.Urllib3Codec())
        HarObject._codecs.append(harlib.codecs.requests.RequestsCodec())
    except Exception as err:
        logger.warning("no requests/urllib3: %s" % repr(err), exc_info=True)

    try:
        import harlib.codecs.httplib
        HarObject._codecs.append(harlib.codecs.httplib.Urllib2Codec())
        HarObject._codecs.append(harlib.codecs.httplib.HttplibCodec())
    except Exception as err:
        logger.warning("no urllib/httplib: %s" % repr(err), exc_info=True)

    try:
        import harlib.codecs.django
        HarObject._codecs.append(harlib.codecs.django.DjangoCodec())
    except Exception as err:
        logger.warning("no django: %s" % repr(err), exc_info=True)

    try:
        import harlib.codecs.default
        HarObject._codecs.append(harlib.codecs.default.DefaultCodec())
    except Exception as err:
        logger.warning("no default: %s" % repr(err), exc_info=True)


initialize_codecs()
