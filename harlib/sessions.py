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
import logging
import os
import requests
import hashlib
import six
from harlib.codecs.requests import RequestsCodec
from . import objects, utils
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

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

    def from_har(self, obj):
        if isinstance(obj, objects.HarFile):
            self._entries.extend(obj.log.entries)
        elif isinstance(obj, objects.HarLog):
            self._entries.extend(obj.entries)
        elif isinstance(obj, objects.HarEntry):
            self._entries.append(obj)
        return self

    def clear(self):
        self._entries = []

    def dump(self, with_content=False, logging_level=None, extra=None, cache=True, with_io=False, **kwargs):
        if logging_level is None:
            logging_level = logging.DEBUG
        nentries = len(self._entries)
        if self._filename and self._entries:
            # add metadata
            if extra is not None:
                if isinstance(extra, dict):
                    extra_data = extra
                else:
                    extra_data = extra.to_json()
                for entry in self._entries:
                    entry._metadata = extra_data

            # make directory
            try:
                dirname = os.path.dirname(self._filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                har = self.to_har(with_content=with_content)
                har_dump = har.dumps(**kwargs)

                if cache:
                    content_hash = self.get_content_hash()
                    cache_dir = os.path.join(dirname, '.harlib')
                    cache_hash_file = os.path.join(cache_dir, content_hash)
                    logger.debug('har cache file: %s' % cache_hash_file)
                    if not os.path.exists(cache_dir):
                        os.makedirs(cache_dir)
                    if not os.path.exists(cache_hash_file):
                        with open(cache_hash_file, 'w') as hf:
                            hf.write(self._filename)
                    else:
                        with open(cache_hash_file, 'r') as ch:
                            previous_filename = ch.read()
                        if os.path.exists(previous_filename):
                            logger.debug('found match cache file')
                            logger.info('%d cached responses in %s' % (nentries, previous_filename,), extra=extra)
                            return previous_filename
                # write file
                with open(self._filename, 'w') as f:
                    f.write(har_dump)
                if cache:
                    with open(cache_hash_file, 'w') as cf:
                        cf.write(self._filename)

            except (IOError, OSError) as err:
                pass
                logger.warning('%s %s' % (type(err), repr(err)))
            except Exception as err:
                pass
                logger.error('%s %s' % (type(err), repr(err)), exc_info=True)

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

    def to_json(self, with_content=False, dict_class=OrderedDict, indent=None):
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

    def get_content_hash(self):
        content = ''
        content_without_reponse_text = ''
        for entry in self._entries:
            content_without_reponse_text += entry.request.method
            content_without_reponse_text += entry.request.url
            try:
                content_without_reponse_text += str(entry.request.postData.text)
            except Exception as err:
                pass
            try:
                content_without_reponse_text += str(entry.request.headers)
            except Exception as err:
                pass
            content_without_reponse_text += str(entry.response.status)
            try:
                content_without_reponse_text += str(entry.response.content.encoding)
            except AttributeError as err:
                pass
            content = content_without_reponse_text
            try:
                if isinstance(entry.response.content.text, six.text_type):
                    content += entry.response.content.text.encode('latin1', 'ignore')
                else:
                    content += entry.response.content.text
            except AttributeError as err:
                pass
            except UnicodeEncodeError as err:
                pass
                logger.warning('UnicodeEncodeError computing text for hash: %s' % err)
            except Exception as err:
                pass
                logger.warning('Exception computing text for hash: %s %s' % (type(err), err,))
        sha_hash = hashlib.new('sha1')
        try:
            if isinstance(content, six.text_type):
                sha_hash.update(content.encode('latin1', 'ignore'))
            else:
                sha_hash.update(content)
        except UnicodeEncodeError as ex:
            logger.warning('UnicodeEncodeError generating hash: %s' % ex)
            sha_hash.update(content_without_reponse_text)
        sha_hash_digest = sha_hash.hexdigest()
        del content_without_reponse_text
        del content
        return sha_hash_digest

    if utils.HAS_XML:
        def to_xml(self, *args, **kwargs):
            '''
            Converts the HAR entries into an XML string
            '''
            indent = kwargs.pop('indent', False)
            d = self.to_json(*args, **kwargs)
            s = utils.xml_dumps(d, indent=indent)
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
            for entry in new_entries:
                if not self.keep_content:
                    self._delete_content(entry)
                if self.keep_socket_options and len(self._kept_sockopts) > 0:
                    entry._socketOptions = map(objects.HarSocketOption, self._kept_sockopts)
                if True: # TODO: make a flag for keeping client options
                    clientOptions = RequestsCodec().decode_HarClientOptions_from_Session(self)
                    entry._clientOptions.__dict__.update(clientOptions)
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
