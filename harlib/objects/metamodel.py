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
import httplib
import json
import logging
import requests
import urllib
import urllib2
from datetime import datetime

logger = logging.getLogger(__name__)

from metaobject import MetaObject

# Superclass for all HAR model objects
class HarObject(MetaObject):

    _ordered = ()

    def __init__(self, obj=None):
        super(HarObject, self).__init__(obj)
        self._ordered = self._ordered or self._required
        self._reserved += ['_ordered']

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

    def to_json(self, dict_class=collections.OrderedDict):
        return super(HarObject, self).to_json(dict_class=dict_class)
