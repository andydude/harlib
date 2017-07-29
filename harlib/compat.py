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

# OrderedDict
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

# requests
try:
    import requests
except ImportError:
    from botocore.vendored import requests

# requests.RequestException
try:
    from requests.exceptions import RequestException
except ImportError:
    from botocore.vendored.requests.exceptions import RequestException

# requests.Request, Response
try:
    from requests.models import Request, Response
except ImportError:
    from botocore.vendored.requests.models import Request, Response

# requests.Session
try:
    from requests.sessions import Session
except ImportError:
    from botocore.vendored.requests.sessions import Session

# requests.adapters.DEFAULT_STREAM
try:
    from requests.adapters import DEFAULT_STREAM
except ImportError:
    DEFAULT_STREAM = False

# urllib3
try:
    import urllib3
except ImportError:
    try:
        from requests.packages import urllib3
    except ImportError:
        from botocore.vendored.requests.packages import urllib3

# urllib3r (urllib3, but prioritize requests)
try:
    from requests.packages import urllib3 as urllib3r
except ImportError:
    try:
        import urllib3 as urllib3r
    except ImportError:
        from botocore.vendored.requests.packages import urllib3 as urllib3r
