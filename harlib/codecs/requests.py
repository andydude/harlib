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
from requests.packages import urllib3 as urllib3r
import collections
import requests
import urllib3
import harlib
import six
from six.moves import http_client
from .httplib import HttplibCodec

KEEP_SIZE = False

class Urllib3Codec(object):

    dict_class = dict
    response_class = urllib3r.response.HTTPResponse
    modules = ['urllib3.response', 'requests.packages.urllib3.response']
    httplib_codec = HttplibCodec()

    def __init__(self):
        pass

    ##########################################################################################
    ## Encoding

    def encode(self, har, raw_class):
        assert raw_class.__module__ in self.modules
        method_name = 'encode_%s_to_%s' % (
            har.__class__.__name__, raw_class.__name__)
        return getattr(self, method_name)(har)

    def encode_HarEntry_to_HTTPResponse(self, har):
        resp = self.encode_HarResponse_to_HTTPResponse(har.response)
        resp.strict = har._clientOptions.failOnError
        resp.decode_content = har._clientOptions.decodeContent
        resp.original_response = self.httplib_codec.encode(har, http_client.HTTPResponse)
        #resp._fp_bytes_read = self._clientOptions.contentRead
        #resp.connection = None
        #resp.pool = None
        return resp

    def encode_HarResponse_to_HTTPResponse(self, har):
        headers = dict(map(harlib.utils.pair_from_obj, har.headers))

        resp = self.response_class(
            body = None,
            headers = headers,
            status = har.status,
            version = harlib.utils.parse_http_version(har.httpVersion),
            reason = har.statusText,
            preload_content = False,
        )

        return resp

    ##########################################################################################
    ## Decoding

    def decode(self, raw, har_class):
        assert raw.__class__.__module__ in self.modules
        method_name = 'decode_%s_from_%s' % (
            har_class.__name__, raw.__class__.__name__)
        return getattr(self, method_name)(raw)

    def decode_HarEntry_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['startedDateTime'] = None
        har['time'] = 0
        har['request'] = raw
        har['response'] = raw
        har['_clientOptions'] = self.dict_class()
        har['_clientOptions']['decodeContent'] = raw.decode_content
        return har

    def decode_HarResponse_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['status'] = raw.status
        har['statusText'] = raw.reason
        har['httpVersion'] = harlib.utils.render_http_version(raw.version)

        har['headers'] = list(raw.headers.items())
        har['cookies'] = []

        har['content'] = self.decode_HarResponseBody_from_HTTPResponse(raw)
        har['redirectURL'] = ''

        if KEEP_SIZE:
            try:
                headers = '\r\n'.join(map(lambda x: '%s: %s' % x, har['headers']))
                har['headersSize'] = len(headers + '\r\n\r\n')
                har['bodySize'] = len(har['content']['text'])
            except:
                har['headersSize'] = -1
                har['bodySize'] = -1
        else:
            har['headersSize'] = -1
            har['bodySize'] = -1

        return har

    def decode_HarResponseBody_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['mimeType'] = raw.headers.get('content-type')
        try:
            text = raw.data
        except:
            text = ''

        har['text'] = text
        har['size'] = len(text)
        har['compression'] = -1
        return har

    def decode_HarRequest_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['method'] = 'UNKNOWN'
        har['url'] = 'UNKNOWN'
        har['headers'] = []
        har['cookies'] = []
        har['queryString'] = []
        har['postData'] = {'mimeType': 'UNKNOWN'}
        return har

    def decode_HarRequestBody_from_HTTPResponse(self, raw):
        return {'mimeType': 'UNKNOWN'}

    #def decode_HarPostDataParam_from_RequestField(self, raw, name=None):
    #if isinstance(obj, urllib3.fields.RequestField):
    #    har['value'] = obj.data
    #    har['fileName'] = obj._filename
    #    har['contentType'] = obj.headers.get('content-type')
    #    if hasattr(obj, 'headers'):
    #        if isinstance(obj.headers, collections.Mapping):
    #            har['_headers'] = map(HarHeader, obj.headers.items())

    #    d = dict()
    #    if name:
    #        d['name'] = name
    #    else:
    #        d['name'] = raw[0]
    #        raw = raw[1:]
    #
    #    pass
    #
    #def decode_HarPostDataParam_from_RequestField(self, raw):
    #    pass
    #
    #def decode_HarPostDataParam_from_tuple(self, raw):
    #    pass

class RequestsCodec(object):

    dict_class = dict
    response_class = requests.Response
    modules = ['requests.models']
    urllib3_codec = Urllib3Codec()

    def __init__(self):
        pass

    ##########################################################################################
    ## Encoding

    def encode(self, har, raw_class):
        assert raw_class.__module__ in self.modules
        raw_type = raw_class.__name__
        har_type = har.__class__.__name__
        return getattr(self, 'encode_%s_to_%s' % (har_type, raw_type))(har)


    def encode_HarEntry_to_Response(self, har):
        from datetime import timedelta
        resp = self.encode_HarResponse_to_Response(har.response)
        resp.url = har.response.redirectURL or har.request.url
        resp.elapsed = timedelta(0, float(har.time)/1000.0)
        resp.encoding = har._clientOptions.charset
        resp.raw = self.urllib3_codec.encode(har, urllib3r.response.HTTPResponse)
        return resp

    def encode_HarResponse_to_Response(self, har):
        ResponseCls = requests.Response
        HeadersCls = requests.structures.CaseInsensitiveDict
        CookiesCls = requests.cookies.RequestsCookieJar
        headers = map(lambda x: x.to_requests(), har.headers)
        cookies = map(lambda x: x.to_requests(), har.cookies)

        resp = ResponseCls()
        resp._content = har.content.text
        resp._content_consumed = True
        resp.status_code = har.status
        resp.reason = har.statusText
        resp.cookies = CookiesCls(collections.OrderedDict(cookies))
        resp.headers = HeadersCls(collections.OrderedDict(headers))
        resp.raw = self.urllib3_codec.encode(har, urllib3r.response.HTTPResponse)
        resp.url = har.redirectURL
        resp.history = []
        #resp.elapsed = 0 # entry.time
        #resp.encoding = None # entry._clientOptions.charset

        return resp

    def encode_HarRequest_to_Request(self, har):
        RequestCls = requests.models.Request
        HeadersCls = dict
        CookiesCls = dict
        headers = map(lambda x: x.to_requests(), har.headers)
        cookies = map(lambda x: x.to_requests(), har.cookies)

        req = RequestCls(method = har.method, url = har.url)
        req.headers = HeadersCls(headers)
        req.cookies = HeadersCls(cookies) if har.cookies else None
        req.params = dict(map(harlib.utils.pair_from_obj, har.queryString))

        if har.postData:
            req.data = dict(map(harlib.utils.pair_from_obj, har.postData.params))

        #req.hooks -- impossible
        #req.auth -- impossible
        #req.params, req.data, req.files = self.body_params()
        return req

    def encode_HarRequest_to_PreparedRequest(self, har):
        RequestCls = requests.models.PreparedRequest
        HeadersCls = dict
        CookiesCls = requests.cookies.RequestsCookieJar
        headers = map(lambda x: x.to_requests(), har.headers) or []
        cookies = map(lambda x: x.to_requests(), har.cookies) or []

        preq = RequestCls()
        preq.method = har.method
        preq.url = har.url
        preq.headers = HeadersCls(collections.OrderedDict(headers))
        preq._cookies = CookiesCls(collections.OrderedDict(cookies))

        if har.postData:
            preq.body = har.postData.text

        #req.hooks -- impossible
        #req.auth -- impossible
        #req.params, req.data, req.files = self.body_params()
        return preq

    ##########################################################################################
    ## Decoding

    def decode(self, raw, har_class):
        assert raw.__class__.__module__ in self.modules
        method_name = 'decode_%s_from_%s' % (har_class.__name__, raw.__class__.__name__)
        method = getattr(self, method_name)
        return method(raw)

    def decode_HarLog_from_Response(self, raw):
        har = []
        if hasattr(raw, 'history') and raw.history and len(raw.history) > 0:
            for tome in raw.history:
                har.append(tome)
        har.append(raw)
        return har

    def decode_HarEntry_from_Response(self, raw):
        from datetime import datetime
        started = (datetime.utcnow() - raw.elapsed).isoformat() + 'Z'

        har = self.dict_class()
        har['startedDateTime'] = None
        har['time'] = raw.elapsed.total_seconds()*1000.0
        har['request'] = raw.request
        har['response'] = raw
        har['cache'] = {}
        har['timings'] = self.decode_HarTimings_from_Response(raw)
        har['connection'] = ''
        har['_clientOptions'] = self.dict_class()
        har['_clientOptions']['charset'] = raw.encoding
        har['_clientOptions']['decodeContent'] = raw.raw.decode_content
        #har['_clientOptions']['contentRead'] = raw.raw._fp_bytes_read
        return har

    def decode_HarResponse_from_Response(self, raw):
        har = self.dict_class()
        har['status'] = raw.status_code
        har['statusText'] = raw.reason
        har['httpVersion'] = harlib.utils.render_http_version(raw.raw.version)

        har['headers'] = list(raw.headers.lower_items())
        har['cookies'] = list(raw.cookies.items()) if raw.cookies else []

        har['content'] = self.decode_HarResponseBody_from_Response(raw)
        har['redirectURL'] = raw.url if raw.url != raw.request.url else ''

        try:
            headers = '\r\n'.join(map(lambda x: '%s: %s' % x, har['headers']))
            har['headersSize'] = len(headers + '\r\n\r\n')
            har['bodySize'] = len(har['content']['text'])
        except:
            har['headersSize'] = -1
            har['bodySize'] = -1

        if hasattr(raw, 'check_result'):
            har['_checkResult'] = raw.check_result
        if hasattr(raw, 'parse_result'):
            har['_parseResult'] = raw.parse_result

        return har

    def decode_HarResponseBody_from_Response(self, raw):
        har = self.dict_class()
        har['mimeType'] = raw.headers.get('content-type')
        try:
            text = raw.text
        except:
            text = ''

        har['text'] = text
        har['size'] = len(text)
        har['compression'] = -1
        return har

    def decode_HarTimings_from_Response(self, raw):
        total = raw.elapsed.total_seconds()*1000.0

        har = self.dict_class()
        har['connect'] = -1
        har['dns'] = -1
        har['receive'] = -1
        har['send']= -1
        har['ssl'] = -1
        har['wait'] = total
        har['_total'] = total
        return har

    def decode_HarRequest_from_Request(self, raw):
        har = self.dict_class()
        har['method'] = raw.method
        har['url'] = raw.url
        har['httpVersion'] = 'HTTP/1.1' # requests uses this default

        if isinstance(raw, requests.models.Request):
            har['headers'] = list(raw.headers.items())
            har['cookies'] = list(raw.cookies.items()) if raw.cookies else []
        elif isinstance(raw, requests.models.PreparedRequest):
            har['headers'] = list(raw.headers.lower_items())
            har['cookies'] = list(raw._cookies.items()) if raw._cookies else []
        else:
            print("unknown request type")

        har['postData'] = self.decode_HarRequestBody(raw)
        har['queryString'] = self.decode_HarQueryStringParams(raw)

        try:
            headers = '\r\n'.join(map(lambda x: '%s: %s' % x, har['headers']))
            har['headersSize'] = len(headers + '\r\n\r\n')
            har['bodySize'] = len(har['postData']['text'])
        except:
            har['headersSize'] = -1
            har['bodySize'] = -1

        if hasattr(raw, 'origin'):
            har['_originURL'] = raw.origin
        if hasattr(raw, 'epid'):
            har['_endpointID'] = raw.epid

        return har

    def decode_HarRequestBody(self, raw):
        if isinstance(raw, requests.models.Request):
            return self.decode_HarRequestBody_from_Request(raw)
        elif isinstance(raw, requests.models.PreparedRequest):
            return self.decode_HarRequestBody_from_PreparedRequest(raw)
        else:
            raise ValueError

    def decode_HarRequestBody_from_Request(self, raw):
        body_params = {}
        body_params.update(raw.data)
        body_params.update(raw.files)

        har = self.dict_class()
        har['mimeType'] = 'UNKNOWN'
        try:
            har['text'] = harlib.utils.encode_query(body_params)
        except:
            har['text'] = ''
        har['_size'] = len(har['text'])

        har['params'] = body_params.items()

        if raw.headers:
            if raw.headers.get('Content-Type'):
                har['mimeType'] = raw.headers.get('Content-Type')

        return har

    def decode_HarRequestBody_from_PreparedRequest(self, raw):
        body_text = raw.body or ''

        har = self.dict_class()
        har['mimeType'] = raw.headers.get('Content-Type')
        har['text'] = body_text or ''
        har['_size'] = len(har['text'])

        try:
            har['params'] = harlib.utils.decode_multipart(har['text'], har['mimeType'])
        except Exception as err:
            #print("e1 %s %s" % (type(err), repr(err)))
            try:
                query = '?' + har['text']
                har['params'] = harlib.utils.decode_query(query)
            except Exception as err:
                #print("e2 %s %s" % (type(err), repr(err)))
                har['params'] = []

        return har

    def decode_HarQueryStringParams(self, raw):
        if isinstance(raw, requests.models.Request):
            return self.decode_HarQueryStringParams_from_Request(raw)
        elif isinstance(raw, requests.models.PreparedRequest):
            return self.decode_HarQueryStringParams_from_PreparedRequest(raw)
        else:
            raise ValueError

    def decode_HarQueryStringParams_from_Request(self, raw):
        return map(harlib.utils.dict_from_pair, raw.params.items())

    def decode_HarQueryStringParams_from_PreparedRequest(self, raw):
        try:
            query = '?' + raw.url.split('?', 1)[1]
            return harlib.utils.decode_query(query)
        except:
            return []

    decode_HarRequest_from_PreparedRequest = decode_HarRequest_from_Request
