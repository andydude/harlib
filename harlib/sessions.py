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
import json
import logging
import os
import requests
from collections import OrderedDict
from . import objects, utils

try:
    from requests.adapters import DEFAULT_STREAM
except ImportError:
    DEFAULT_STREAM = False

logger = logging.getLogger(__name__)

class HarSocketManager(object):

    def __init__(self, session):
        pass

    def __enter__(self):
        pass

    def __exit__(self):
        pass

class HarSessionMixin(object):

    def __init__(self, filename=None):
        object.__init__(self)
        self._entries = []
        self._filename = str(filename) if filename else ''
        self._kept_sockopts = []
        self.keep_entries = True
        self.keep_content = True
        self.keep_client_options = False
        self.keep_server_options = False
        self.keep_socket_options = False

    def clear(self):
        self._entries.clear()

    def dump(self, with_content=False, logging_level=None, extra=None, **kwargs):
        if logging_level is None:
            logging_level = logging.DEBUG
        nentries = len(self._entries)
        if self._filename and self._entries:

            # make directory
            try:
                dirname = os.path.dirname(self._filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
            except (IOError, OSError) as err:
                logger.warning('%s %s' % (type(err), repr(err)))
            except Exception as err:
                logger.error('%s %s' % (type(err), repr(err)))

            # write file
            with open(self._filename, 'w') as f:
                har = self.to_har(with_content=with_content)
                s = har.dumps(**kwargs)
                f.write(s)

        VIRTUAL_ENV = os.environ.get('VIRTUAL_ENV')
        filename = self._filename
        if VIRTUAL_ENV and filename and filename.startswith(VIRTUAL_ENV):
            filename = '${VIRTUAL_ENV}' + filename[len(VIRTUAL_ENV):]
        logger.log(logging_level, 'Dumped %d responses to %s' % (nentries, filename), extra=extra)
        return str(self._filename)

    def dumps(self, with_content=False, **kwargs):
        har = self.to_har(with_content=with_content)
        s = har.dumps(**kwargs)
        return s

    def to_json(self, with_content=False, dict_class=OrderedDict):
        '''
        Converts the HAR entries into a dictionary
        '''
        har = self.to_har(with_content=with_content)
        return har.to_json(dict_class=dict_class)

    def to_har(self, with_content=False):
        '''
        Converts the HAR entries into a model object
        '''
        har = objects.HarFile([])
        if self._filename:
            har.log.entries = self._entries

        if with_content:
            return har

        for entry in har.log.entries:
            self._delete_content(entry)

        return har

    def _delete_content(self, entry):
        try:
            del entry.request.postData.text
            del entry.request.postData.encoding
        except:
            pass

        try:
            del entry.response.content.text
            del entry.response.content.encoding
        except:
            pass

    if utils.HAS_XML:
        def to_xml(self, *args, **kwargs):
            '''
            Converts the HAR entries into an XML string
            '''
            d = self.to_json(*args, **kwargs)
            s = utils.xml_dumps(d)
            return s

    if utils.HAS_YAML:
        def to_yaml(self, *args, **kwargs):
            '''
            Converts the HAR entries into a YAML string
            '''
            d = self.to_json(*args, **kwargs)
            s = utils.yaml_dumps(d)
            return s

    def _keep_entries(self, resp):
        if self._filename is not None:
            new_entries = objects.HarLog(resp).entries
            if not self.keep_content:
                for entry in new_entries:
                    self._delete_content(entry)
            if self.keep_socket_options and len(self._kept_sockopts) > 0:
                for entry in new_entries:
                    entry._socketOptions = map(objects.HarSocketOption, self._kept_sockopts)
            self._entries.extend(new_entries)

    def _update_entry(self, attr, value, index = -1):
        try:
            setattr(self._entries[index], attr, value)
        except Exception as err:
            pass

    def request(self, method, url, **kwargs):

        if self.keep_socket_options:
            # force stream=True
            stream = kwargs.get('stream', DEFAULT_STREAM)
            kwargs['stream'] = True

        resp = requests.Session.request(self, method, url, **kwargs)

        if self.keep_socket_options:
            self._kept_sockopts = utils.get_sockopts_from_response(resp)
            # reimplement stream=False
            if not stream:
                resp.content

        if self.keep_entries:
            self._keep_entries(resp)

        return resp

class HarSession(HarSessionMixin, requests.Session):

    def __init__(self, filename=None):
        requests.Session.__init__(self)
        HarSessionMixin.__init__(self, filename)
