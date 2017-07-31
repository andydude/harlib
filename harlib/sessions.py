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
import logging
import os
import hashlib
import six
from .codecs.requests import RequestsCodec
from .compat import OrderedDict
from .compat import requests
from .compat import DEFAULT_STREAM
from . import objects, utils

try:
    from typing import (
        Any, BinaryIO, Dict, List,
        NamedTuple, Optional, TextIO, Tuple)
except ImportError:
    pass

logger = logging.getLogger(__name__)


class HarSessionMixin(object):

    def __init__(self, filename=None):
        # type: (str) -> None
        object.__init__(self)
        self._entries = []
        self._filename = str(filename) if filename else ''
        self._cache_filename = ''
        self._kept_sockopts = []
        self.keep_entries = True
        self.keep_content = True
        self.keep_client_options = False
        self.keep_server_options = False
        self.keep_socket_options = False

    def from_har(self, obj):
        # type: (Dict) -> HarSessionMixin
        if isinstance(obj, objects.HarFile):
            self._entries.extend(obj.log.entries)
        elif isinstance(obj, objects.HarLog):
            self._entries.extend(obj.entries)
        elif isinstance(obj, objects.HarEntry):
            self._entries.append(obj)
        return self

    def clear(self):
        # type: () -> None
        self._entries = []

    def _dump_metadata(
            self, with_content=False,
            logging_level=None,
            extra=None, cache=True,
            with_io=False, **kwargs):
        # type: (bool, Optional[int], Any, bool, bool, **Any) -> None
        if extra is not None:
            if isinstance(extra, dict):
                extra_data = extra
            else:
                extra_data = extra.to_json()
            for entry in self._entries:
                entry._metadata = extra_data

    def _dump_check_dir(
            self, with_content=False,
            logging_level=None,
            extra=None, cache=True,
            with_io=False, **kwargs):
        # type: (bool, Optional[int], Any, bool, bool, **Any) -> None
        dirname = os.path.dirname(self._filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def _dump_check_cache(
            self, with_content=False,
            logging_level=None,
            extra=None, cache=True,
            with_io=False, **kwargs):
        # type: (bool, Optional[int], Any, bool, bool, **Any) -> None
        if cache:
            content_hash = self.get_content_hash()
            cache_dir = os.path.join(
                os.path.dirname(self._filename), '.harlib')
            self._cache_filename = os.path.join(cache_dir, content_hash)
            logger.debug('har cache file: %s' % self._cache_filename)
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            if not os.path.exists(self._cache_filename):
                with open(self._cache_filename, 'w') as hf:
                    hf.write(self._filename)
            else:
                with open(self._cache_filename, 'r') as ch:
                    previous_filename = ch.read()
                if os.path.exists(previous_filename):
                    logger.debug('found match cache file')
                    logger.info('%d cached responses in %s' %
                                (len(self._entries), previous_filename,),
                                extra=extra)
                    return previous_filename

    def _dump_write_file(
            self, with_content=False,
            logging_level=None,
            extra=None, cache=True,
            with_io=False, **kwargs):
        # type: (bool, Optional[int], Any, bool, bool, **Any) -> None
        har = self.to_har(with_content=with_content)
        har_dump = har.dumps(**kwargs)
        with open(self._filename, 'w') as f:
            f.write(har_dump)
        if cache:
            with open(self._cache_filename, 'w') as writer:
                writer.write(self._filename)

    def _dump_summarize(
            self, with_content=False,
            logging_level=None,
            extra=None, cache=True,
            with_io=False, **kwargs):
        # type: (bool, Optional[int], Any, bool, bool, **Any) -> None
        if logging_level is None:
            logging_level = logging.DEBUG
        VIRTUAL_ENV = os.environ.get('VIRTUAL_ENV')
        filename = self._filename
        if VIRTUAL_ENV and filename and filename.startswith(VIRTUAL_ENV):
            filename = '${VIRTUAL_ENV}' + filename[len(VIRTUAL_ENV):]
        logger.log(logging_level, 'Dumped %d responses to %s' %
                   (len(self._entries), filename), extra=extra)

    def dump(self, with_content=False,
             logging_level=None, **kwargs):
        # type: (bool, Optional[int], **Any) -> None
        if logging_level is None:
            logging_level = logging.DEBUG
        if self._filename and self._entries:
            try:
                # Refactored this because of its original complexity.
                # C901 'HarSessionMixin.dump' is too complex (16)
                self._dump_metadata(with_content, logging_level, **kwargs)
                self._dump_check_dir(with_content, logging_level, **kwargs)
                self._dump_check_cache(with_content, logging_level, **kwargs)
                self._dump_write_file(with_content, logging_level, **kwargs)
                self._dump_summarize(with_content, logging_level, **kwargs)
            except (IOError, OSError) as err:
                pass
                logger.warning('%s %s' % (type(err), repr(err)))
            except Exception as err:
                pass
                logger.error('%s %s' % (type(err), repr(err)), exc_info=True)
        return str(self._filename)

    def dumps(self, with_content=False, **kwargs):
        har = self.to_har(with_content=with_content)
        s = har.dumps(**kwargs)
        return s

    def to_json(self, with_content=False, dict_class=OrderedDict, indent=None):
        # type: (bool, type, Optional[int]) -> Dict
        '''
        Converts the HAR entries into a dictionary
        '''
        har = self.to_har(with_content=with_content)
        return har.to_json(dict_class=dict_class)

    def to_har(self, with_content=False):
        # type: (bool) -> objects.HarFile
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
        # type: (HarEntry) -> None
        try:
            del entry.request.postData.text
            del entry.request.postData.encoding
        except Exception:
            pass

        try:
            del entry.response.content.text
            del entry.response.content.encoding
        except Exception:
            pass

    def get_content_hash_from_request(self, request, writer):
        # type: (HarRequest, TextIO) -> None
        writer.write(request.method)
        writer.write(request.url)
        try:
            writer.write(six.text_type(request.postData.text))
        except Exception:
            pass
        try:
            writer.write(six.text_type(request.headers))
        except Exception:
            pass

    def get_content_hash_from_response(self, response, writer):
        # type: (HarResponse, TextIO) -> None
        writer.write(six.text_type(response.status))
        try:
            writer.write(six.text_type(response.content.encoding))
        except AttributeError:
            pass
        try:
            if isinstance(response.content.text, six.text_type):
                writer.write(response.content.text)
            else:
                writer.write(response.content.text.decode(
                    'latin1', 'ignore'))
        except Exception:
            pass

    def get_content_hash(self):
        # type: () -> str
        content = ''
        writer = six.StringIO()
        for entry in self._entries:
            self.get_content_hash_from_request(entry.request, writer)
            self.get_content_hash_from_response(entry.response, writer)
        content = writer.getvalue().encode('latin1', 'ignore')
        sha_hash = hashlib.new('sha1')
        try:
            if isinstance(content, six.text_type):
                sha_hash.update(content.encode('latin1', 'ignore'))
            else:
                sha_hash.update(content)
        except UnicodeEncodeError as ex:
            logger.warning('UnicodeEncodeError generating hash: %s' % ex)
        sha_hash_digest = sha_hash.hexdigest()
        del writer
        del content
        return sha_hash_digest

    if utils.HAS_XML:
        def to_xml(self, *args, **kwargs):
            # type: (*Any, **Any) -> str
            '''
            Converts the HAR entries into an XML string
            '''
            indent = kwargs.pop('indent', False)
            d = self.to_json(*args, **kwargs)
            s = utils.xml_dumps(d, indent=indent)
            return s

    if utils.HAS_YAML:
        def to_yaml(self, *args, **kwargs):
            # type: (*Any, **Any) -> str
            '''
            Converts the HAR entries into a YAML string
            '''
            d = self.to_json(*args, **kwargs)
            s = utils.yaml_dumps(d)
            return s

    def _keep_entries(self, resp):
        # type: (requests.Response) -> None
        if self._filename is not None:
            new_entries = objects.HarLog(resp).entries
            for entry in new_entries:
                if not self.keep_content:
                    self._delete_content(entry)
                if self.keep_socket_options and len(self._kept_sockopts) > 0:
                    entry._socketOptions = map(
                        objects.HarSocketOption, self._kept_sockopts)
                if True:  # TODO: make a flag for keeping client options
                    clientOptions = RequestsCodec().\
                        decode_HarClientOptions_from_Session(self)
                    entry._clientOptions.__dict__.update(clientOptions)
            self._entries.extend(new_entries)

    def _update_entry(self, attr, value, index=-1):
        # type: (str, Any, int) -> None
        try:
            setattr(self._entries[index], attr, value)
        except Exception:
            pass

    def request(self, method, url, **kwargs):
        # type: (str, str, **Any) -> requests.Response

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
        # type: (Optional[str]) -> None
        requests.Session.__init__(self)
        HarSessionMixin.__init__(self, filename)
