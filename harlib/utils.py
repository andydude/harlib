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
import socket
import struct
import json
import six
from collections import Mapping
from .compat import OrderedDict
from six.moves import map


def render_http_version(num):
    '''
    Function from ._httpVersionNumber to .httpVersion
    '''
    return 'HTTP/%s' % str(float(num) / 10.0)


def parse_http_version(s):
    '''
    Function from .httpVersion to ._httpVersionNumber
    '''
    return int(float(s.split('/', 1)[1]) * 10.0)


def parse_pair(item):
    if '=' not in item:
        item += '='
    if '&' in item:
        raise ValueError(repr(item), 'must split on "&" first')
    name, value = item.split('=')
    return {'name': name, 'value': value}


def dict_from_pair(pair):
    return {'name': pair[0], 'value': pair[1]}


def pair_from_dict(data):
    return (data['name'], data['value'])


def pair_from_obj(data):
    return (data.name, data.value)


def decode_json(o, **kwargs):
    d = o
    if not isinstance(d, dict):
        d = json.loads(d)
    har = list(map(dict_from_pair, list(d.items())))
    return har


def decode_multipart(o, content_type, **kwargs):
    har = []

    try:
        if isinstance(o, six.string_types):
            import multipart
            content_type, options = multipart.parse_options_header(
                content_type)
            assert content_type == 'multipart/form-data'
            stream = six.BytesIO(o)
            boundary = six.binary_type(options.get('boundary'))
            assert boundary
            for part in multipart.MultipartParser(stream, boundary, len(o),
                                                  **kwargs):
                if part.filename or not part.is_buffered():
                    param = {'name': part.name, 'value': str(part.value),
                             'filename': str(part.filename)}
                else:  # TODO: Big form-fields are in the files dict. really?
                    param = {'name': part.name, 'value': str(part.value)}
                har.append(param)
    except Exception:
        pass

    return har


def decode_query(o):
    har = []
    if isinstance(o, six.string_types):
        from requests.packages import urllib3 as urllib3r
        query = urllib3r.util.parse_url(o).query
        if query is None:
            return []
        pairs = query.split('&')
        pairs = [it for it in pairs if it != '']
        har = list(map(parse_pair, pairs))
    return har


def encode_query(d):
    har = ''
    if isinstance(d, dict):
        d = list(d.items())
    if isinstance(d, list):
        if isinstance(d[0], Mapping):
            d = [(p['name'], p['value']) for p in d]
        for name, value in d:
            har += '&' + str(name) + '=' + str(value)
    if har != '':
        return har[1:]
    else:
        return ''


def get_sockopts_from_response(resp):
    '''
    Warning: if you are using this with requests, then you MUST set stream=True
    in the request for this to work, then after running this function, you can
    reimplement the will_close logic and read the socket to a buffer.
    '''
    scheme = resp.request.url.split(':', 1)[0]

    if scheme == 'http':
        sock = resp.raw._fp.fp._sock
    elif scheme == 'https':
        sock = resp.raw._fp.fp._sock._sock
    else:
        raise ValueError("unrecognized scheme %s" % scheme)

    sockopts = get_sockopts_from_socket(sock)
    return sockopts


def get_sockopts_from_socket(sock):
    '''
    '''

    # (level, name, format, bytesize)
    sockopts = [
        ('IPPROTO_IP', 'IP_HDRINCL', None, 0),
        ('IPPROTO_IP', 'IP_TOS', None, 0),
        ('IPPROTO_TCP', 'TCP_KEEPALIVE', None, 0), 		# QNX
        ('IPPROTO_TCP', 'TCP_NODELAY', None, 0),		# Linux
        ('SOL_SOCKET', 'SO_ACCEPTCONN', None, 0),		# SUSv4, Linux
        ('SOL_SOCKET', 'SO_BINDTODEVICE', None, 0),		# Linux, QNX
        ('SOL_SOCKET', 'SO_BROADCAST', None, 0),		# SUSv4, Linux
        ('SOL_SOCKET', 'SO_BSDCOMPAT', None, 0),		# Linux
        ('SOL_SOCKET', 'SO_BSP_STATE', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_CONDITIONAL_ACCEPT', None, 0), 	# Windows
        ('SOL_SOCKET', 'SO_CONNDATA', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_CONNDATALEN', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_CONNECT_TIME', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_CONNOPT', None, 0), 			# Windows
        ('SOL_SOCKET', 'SO_CONNOPTLEN', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_DEBUG', None, 0),			# SUSv4, Linux
        ('SOL_SOCKET', 'SO_DISCDATA', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_DISCDATALEN', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_DISCOPT', None, 0), 			# Windows
        ('SOL_SOCKET', 'SO_DISCOPTLEN', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_DONTLINGER', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_DONTROUTE', None, 0),		# SUSv4, Linux
        ('SOL_SOCKET', 'SO_ERROR', None, 0),			# SUSv4, Linux
        ('SOL_SOCKET', 'SO_EXCLUSIVEADDRUSE', None, 0), 	# Windows
        ('SOL_SOCKET', 'SO_GROUP_ID', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_GROUP_PRIORITY', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_KEEPALIVE', None, 0),		# SUSv4
        ('SOL_SOCKET', 'SO_LINGER', 'll', 8),			# SUSv4
        ('SOL_SOCKET', 'SO_MARK', None, 0), 			# Linux
        ('SOL_SOCKET', 'SO_MAXDG', None, 0), 			# Windows
        ('SOL_SOCKET', 'SO_MAXPATHDG', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_MAX_MSG_SIZE', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_NO_CHECK', None, 0),			# Linux
        ('SOL_SOCKET', 'SO_OOBINLINE', None, 0),		# SUSv4
        ('SOL_SOCKET', 'SO_OPENTYPE', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_PASSCRED', None, 0),			# Linux
        ('SOL_SOCKET', 'SO_PASSSEC', None, 0),			# Linux
        ('SOL_SOCKET', 'SO_PEERCRED', None, 0),			# Linux
        ('SOL_SOCKET', 'SO_PEERSEC', None, 0),			# Linux
        ('SOL_SOCKET', 'SO_PORT_SCALABILITY', None, 0), 	# Windows
        ('SOL_SOCKET', 'SO_PRIORITY', None, 0),			# Linux
        ('SOL_SOCKET', 'SO_PROTOCOL_INFO', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_PROTOCOL_INFOA', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_PROTOCOL_INFOW', None, 0), 		# Windows
        ('SOL_SOCKET', 'SO_RCVBUF', None, 0),			# SUSv4
        ('SOL_SOCKET', 'SO_RCVBUFFORCE', None, 0),		# Linux
        ('SOL_SOCKET', 'SO_RCVLOWAT', None, 0),			# SUSv4
        ('SOL_SOCKET', 'SO_RCVTIMEO', 'l4xi', 16),	   	# SUSv4
        ('SOL_SOCKET', 'SO_REUSEADDR', None, 0), 		# SUSv4, Linux, QNX, Windows
        ('SOL_SOCKET', 'SO_REUSEPORT', None, 0), 		# Linux, QNX
        ('SOL_SOCKET', 'SO_SNDBUF', None, 0),			# SUSv4
        ('SOL_SOCKET', 'SO_SNDBUFFORCE', None, 0),		# Linux
        ('SOL_SOCKET', 'SO_SNDLOWAT', None, 0),			# SUSv4
        ('SOL_SOCKET', 'SO_SNDTIMEO', 'l4xi', 16),		# SUSv4
        ('SOL_SOCKET', 'SO_TIMESTAMP', None, 0), 		# Linux, QNX
        ('SOL_SOCKET', 'SO_TYPE', None, 0),			# SUSv4, Linux
        ('SOL_SOCKET', 'SO_UPDATE_ACCEPT_CONTEXT', None, 0), 	# Windows
        ('SOL_SOCKET', 'SO_UPDATE_CONNECT_CONTEXT', None, 0), 	# Windows
        ('SOL_SOCKET', 'SO_USELOOPBACK', None, 0), 		# QNX
    ]

    sockattrs = [
        ('SOL_SOCKET', 'SO_DOMAIN', sock.family),
        ('SOL_SOCKET', 'SO_PROTOCOL', sock.proto),
        ('SOL_PYTHON', 'PYTHON_FILENO', sock.fileno()),
        ('SOL_PYTHON', 'PYTHON_TIMEOUT', sock.gettimeout()),
    ]

    opts = []

    for sockopt in sockopts:
        level, name, fmt, size = sockopt
        try:
            if size:
                value = sock.getsockopt(getattr(socket, level),
                                        getattr(socket, name),
                                        size)
                value = struct.unpack(fmt, value)
            else:
                value = sock.getsockopt(getattr(socket, level),
                                        getattr(socket, name))
        except Exception:
            pass
        else:
            opt = OrderedDict()
            opt["level"] = level
            opt["name"] = name
            opt["value"] = value
            opts.append(opt)

    for level, name, value in sockattrs:
        opt = OrderedDict()
        opt["level"] = level
        opt["name"] = name
        opt["value"] = value
        opts.append(opt)

    return opts


# XML stuff
try:
    import bs4

    xml_plural_to_singular = {
        'entries': 'entry',
        'headers': 'header',
        'pages': 'page',
        'params': 'param',
        'queryString': 'param',
        'cache': 'cacheEntry',
        '_socketOptions': '_socketOption',
    }

    def xml_dump_named_tree(key, value, soup=None, default=str):
        tag = soup.new_tag(name=key)
        if isinstance(value, list):
            tag.contents = []
            key2 = xml_plural_to_singular.get(key, 'li')
            for v in value:
                tag.append(xml_dump_named_tree(key2, v, soup=soup,
                                               default=default))
        elif isinstance(value, dict):
            tag.contents = []
            for k, v in value.items():
                tag.append(xml_dump_named_tree(k, v, soup=soup,
                                               default=default))
        else:
            tag.append(soup.new_string(default(value)))
        return tag

    def xml_dumps(d, indent=False):
        soup = bs4.BeautifulSoup('<root></root>')
        tag = xml_dump_named_tree('root', d, soup=soup)
        tag = list(tag.children)[0]
        if indent:
            s = tag.prettify(formatter='xml')
        else:
            s = str(tag)
        return s

    HAS_XML = True
except ImportError:
    HAS_XML = False
    bs4 = None

# YAML stuff
try:
    import yaml

    def yaml_represent_ordered_mapping(self, tag, mapping, flow_style=None):
        value = []
        node = yaml.MappingNode(tag, value, flow_style=flow_style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        if hasattr(mapping, 'items'):
            mapping = list(mapping.items())
        for item_key, item_value in mapping:
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            if not (isinstance(node_key, yaml.ScalarNode)
                    and not node_key.style):
                best_style = False
            if not (isinstance(node_value, yaml.ScalarNode)
                    and not node_value.style):
                best_style = False
            value.append((node_key, node_value))
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node

    yaml.representer.BaseRepresenter.represent_mapping = \
        yaml_represent_ordered_mapping
    yaml.representer.Representer.add_representer(
        OrderedDict, yaml.representer.SafeRepresenter.represent_dict)

    def yaml_dumps(d):
        return yaml.dump(d, indent=2, default_flow_style=False)

    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None
