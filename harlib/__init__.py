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
from __future__ import print_function
from datetime import datetime
from metaobject import parse_commit
import os.path

__repo_path__ = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
__title__ = os.path.basename(__repo_path__)
(__date__, __time__, __version__, __version_tag__) = parse_commit(__repo_path__)
__credits__ = u'Copyright \xa9 %s Andrew Robbins, All rights reserved.' % (__date__.split('-')[0])
__homepage_url__ = 'https://github.com/andydude/%s/blob/%s/README.md' % (__title__, __version_tag__)
__download_url__ = 'https://github.com/andydude/%s/archive/%s.zip' % (__title__, __version_tag__)

if __name__ == '__main__':
    print("credits:", __credits__)
    print("datetime:", __date__, __time__)
    print("title:", __title__)
    print("version:", __version__)
    print("version_tag:", __version_tag__)
    print("download_url:", __download_url__)
    print("url:", __homepage_url__)

else:
    # only import after installing six
    try:
        import six
        from .objects import *
    except ImportError:
        pass

    # only import HarSession if requests is installed
    try:
        import requests
        from .sessions import HarSessionMixin, HarSession
    except ImportError:
        pass
