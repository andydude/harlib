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

import wsgiref.handlers
import django.http.request
import django.http.response
import os
from . import utils


class DjangoCodec(object):

    dict_class = dict
    request_class = django.http.request.HttpRequest
    response_class = django.http.response.HttpResponse
    modules = [
        'django.http.request',
        'django.http.response',
        'django.core.handlers.wsgi',
        'django.template.response',
        'rest_framework.request',
        'rest_framework.response',
    ]

    def __init__(self):
        object.__init__(self)

    # Encoding

    def encode(self, har, raw_class):
        assert raw_class.__module__ in self.modules
        method_name = 'encode_%s_to_%s' % (
            har.__class__.__name__, raw_class.__name__)
        return getattr(self, method_name)(har)

    def encode_HarRequest_to_HttpRequest(self, har):
        req = self.request_class()
        return req

    def encode_HarResponse_to_HttpResponse(self, har):
        resp = self.response_class()
        return resp

    # Decoding

    def decode(self, raw, har_class):
        assert raw.__class__.__module__ in self.modules
        method_name = 'decode_%s_from_%s' % (
            har_class.__name__, raw.__class__.__name__)
        return getattr(self, method_name)(raw)

    def decode_HarRequest_from_Request(self, raw):
        return self.decode_HarRequest_from_HttpRequest(raw._request)

    def decode_HarRequest_from_HttpRequest(self, raw):
        version = os.environ.get('SERVER_PROTOCOL', 'HTTP/1.1')
        url = '%s://%s%s' % (os.environ.get('wsgi.url_scheme', 'http'),
                             raw.get_host(), raw.get_full_path())

        har = self.dict_class()
        har['method'] = raw.method
        har['url'] = url
        har['httpVersion'] = version
        har['headers'] = self.decode_HarHeaders_from_HttpRequest(raw)
        har['cookies'] = self.decode_HarCookies_from_HttpRequest(raw)
        har['postData'] = raw
        har['queryString'] = \
            self.decode_HarQueryStringParams_from_HttpRequest(raw)
        har['headersSize'] = -1
        har['bodySize'] = -1
        return har

    def decode_HarResponse_from_HttpResponse(self, raw):
        version = 'HTTP/%s' % wsgiref.handlers.BaseHandler.http_version
        har = self.dict_class()
        har['status'] = raw.status_code
        har['statusText'] = raw.reason_phrase
        har['httpVersion'] = version
        har['headers'] = self.decode_HarHeaders_from_HttpResponse(raw)
        har['cookies'] = self.decode_HarCookies_from_HttpResponse(raw)
        har['content'] = raw
        har['redirectURL'] = ''
        har['headersSize'] = -1
        har['bodySize'] = -1
        return har

    def decode_HarCookies_from_HttpRequest(self, raw):
        return raw.COOKIES.items()

    def decode_HarHeaders_from_HttpRequest(self, raw):
        headers = []
        for k, v in raw.META.items():
            if k.startswith('HTTP_'):
                k = k[len('HTTP_'):].replace('_', '-').title()
                headers.append((k, v))
        return headers

    def decode_HarCookies_from_HttpResponse(self, raw):
        return []

    def decode_HarHeaders_from_HttpResponse(self, raw):
        headers = map(lambda i: (i[1][0], i[1][1]), raw._headers.items())
        return headers

    def decode_HarRequestBody_from_HttpRequest(self, raw):
        har = self.dict_class()
        har['mimeType'] = 'UNKNOWN'
        har['text'] = raw.body
        har['_size'] = len(har['text'])
        try:
            query = '?' + har['text']
            har['params'] = utils.decode_query(query)
        except:
            har['params'] = []
        return har

    def decode_HarQueryStringParams_from_HttpRequest(self, raw):
        return []

    def decode_HarResponseBody_from_HttpResponse(self, raw):
        har = self.dict_class()
        har['mimeType'] = raw._headers.get('content-type')[1]
        har['text'] = raw.content
        har['size'] = len(har['text'])
        har['compression'] = -1
        return har

    decode_HarRequest_from_WSGIRequest = \
        decode_HarRequest_from_HttpRequest
    decode_HarRequestBody_from_WSGIRequest = \
        decode_HarRequestBody_from_HttpRequest
    decode_HarResponse_from_HttpResponseBadRequest = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_HttpResponseForbidden = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_HttpResponseGone = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_HttpResponseNotAllowed = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_HttpResponseNotFound = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_HttpResponseNotModified = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_HttpResponsePermanentRedirect = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_HttpResponseRedirect = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_HttpResponseServerError = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_Response = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_SimpleTemplateResponse = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponse_from_TemplateResponse = \
        decode_HarResponse_from_HttpResponse
    decode_HarResponseBody_from_HttpResponseBadRequest = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_HttpResponseForbidden = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_HttpResponseGone = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_HttpResponseNotAllowed = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_HttpResponseNotFound = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_HttpResponseNotModified = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_HttpResponsePermanentRedirect = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_HttpResponseRedirect = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_HttpResponseServerError = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_Response = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_SimpleTemplateResponse = \
        decode_HarResponseBody_from_HttpResponse
    decode_HarResponseBody_from_TemplateResponse = \
        decode_HarResponseBody_from_HttpResponse
