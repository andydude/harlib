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
from .objects import HarObject, HarFile, HarLog, HarEntry, HarResponse, HarRequest
import collections, json

def dump(o, f):
    assert(isinstance(o, HarObject))
    assert(isinstance(f, file))
    o.dump(f)

def dumps(o):
    assert(isinstance(o, HarObject))
    return o.dumps()

def dumpd(o):
    assert(isinstance(o, HarObject))
    return o.to_json()

def loadd(d):
    assert(isinstance(d, collections.Mapping))
    if 'log' in d:
        return HarFile(d)
    elif 'entries' in d:
        return HarLog(d)
    elif 'time' in d:
        return HarEntry(d)
    elif 'status' in d or 'statusText' in d or 'content' in d:
        return HarResponse(d)
    elif 'method' in d or 'url' in d or 'queryString' in d:
        return HarRequest(d)
    else:
        raise ValueError("unrecognized HAR content", d)

def loads(s):
    assert(isinstance(s, (bytes, str, unicode)))
    d = json.loads(s)
    return loadd(d)

def load(f):
    assert(isinstance(f, file))
    d = json.load(f)
    return loadd(d)
