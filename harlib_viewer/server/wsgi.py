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
from django.core.wsgi import get_wsgi_application
from os import environ
'''
harlib - HTTP Archive (HAR) format library
'''
'''
WSGI config for harlib_viewer.server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
'''

environ.setdefault('DJANGO_SETTINGS_MODULE',
                   'harlib_viewer.server.settings')
application = get_wsgi_application()
