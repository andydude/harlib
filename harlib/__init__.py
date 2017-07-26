#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014-2017, Andrew Robbins, All rights reserved.
#
# This library ("it") is free software; it is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; you can redistribute it and/or
# modify it under the terms of LGPLv3 <https://www.gnu.org/licenses/lgpl.html>.
'''
harlib - HTTP Archive (HAR) format library
'''
from __future__ import absolute_import
from __future__ import print_function
from metaobject import parse_commit
import os.path
import logging
logger = logging.getLogger(__name__)

__repo_path__ = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
__title__ = os.path.basename(__repo_path__)
(_, _, __version__, __version_tag__) = parse_commit(__repo_path__)
__homepage_url__ = 'https://github.com/andydude/%s/blob/%s/README.md' % (__title__, __version_tag__)
__download_url__ = 'https://github.com/andydude/%s/archive/%s.zip' % (__title__, __version_tag__)

if __name__ == '__main__':
    print("title:", __title__)
    print("version:", __version__)
    print("version_tag:", __version_tag__)

else:
    # flake8: noqa

    # only import after installing six
    try:
        import six  
        from .objects import (
            HarFile, HarLog, 
            HarObject, HarEntry,
            HarResponse, HarRequest)  # noqa: F401
    except ImportError as err:
        logger.error(repr(err), exc_info=True)

    # only import HarSession if requests is installed
    try:
        import requests  
        from .sessions import (
            HarSessionMixin,
            HarSession)  # noqa: F401
    except ImportError as err:
        logger.error(repr(err), exc_info=True)
