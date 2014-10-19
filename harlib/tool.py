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
import collections
import json

import one.utils

def by_name(har):
    return har['name']

def sorted_har_request_body(har):
    if har.has_key('params'):
        har['params'] = sorted(har['params'], key=by_name)
    return har

def sorted_har_request(har):
    har['headers'] = sorted(har['headers'], key=by_name)
    if har.has_key('cookies'):
        har['cookies'] = sorted(har['cookies'], key=by_name)
    if har.has_key('queryString'):
        har['queryString'] = sorted(har['queryString'], key=by_name)    
    if har.has_key('postData'):
        har['postData'] = sorted_har_request_body(har['postData'])
    return har

def sorted_har_response(har):
    har['headers'] = sorted(har['headers'], key=by_name)
    if har.has_key('cookies'):
        har['cookies'] = sorted(har['cookies'], key=by_name)
    return har

def sorted_har_entry(har):
    har['request'] = sorted_har_request(har['request'])
    har['response'] = sorted_har_request(har['response'])
    return har

def sorted_har(har):
    for i, entry in enumerate(har['log']['entries']):
        har['log']['entries'][i] = sorted_har_entry(entry)
    return har

def har_sort_main():
    import sys
    filename = sys.argv[1]
    d = json.loads(one.utils.file_slurp(filename), object_pairs_hook=collections.OrderedDict)
    d = sorted_har(d)
    print(json.dumps(d, indent=2, default=str, separators=(',',': ')))

main = har_sort_main
if __name__ == '__main__':
    main()
