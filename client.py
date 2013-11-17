#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Chat in HTTP protocol.
"""

import httplib
from BaseHTTPServer import BaseHTTPRequestHandler
from cStringIO import StringIO

__all__ = ['ChatHTTPClient']

class ChatHTTPClient(object):
    r"""Send a request message, and then receive a response message.

    >>> conn = ChatHTTPClient('www.python.org')
    >>> conn.request('GET / HTTP/1.1\r\nHost: www.python.org\r\n\r\n')
    (True, '')
    >>> conn.response()
    'HTTP/1.1 200 OK\r\ncontent-length: 20490\r\naccept-ranges: bytes\r\nvary: Accept-Encoding\r\nserver: Apache/2.2.16 (Debian)\r\nlast-modified: Fri, 15 Nov 2013 12:27:01 GMT\r\netag: "105800d-500a-4eb3650ab2f40"\r\ndate: Fri, 15 Nov 2013 16:36:33 GMT\r\ncontent-type: text/html\r\n\r\n'
    """
    def __init__(self, host, port=80):
        self.conn = httplib.HTTPConnection(host, port)

    def __del__(self):
        self.conn.close()

    def request(self, message):
        req = HTTPRequestParser(message)
        if req.error: # error occurs when parsing `message`
            return (False, req.error[1])
        self.conn.request(req.method, req.url, req.body, req.headers)
        return (True, '')

    def response(self, show_body=False):
        res = self.conn.getresponse()
        start_line = '%s %s %s' % ({10: 'HTTP/1.0', 11: 'HTTP/1.1'}[res.version], res.status, res.reason)
        headers = '\r\n'.join('%s: %s' % header for header in res.getheaders())
        body = res.read()
        return '%s\r\n%s\r\n\r\n%s' % (start_line, headers, body if show_body else '')

class HTTPRequestParser(BaseHTTPRequestHandler):
    """"Parse the request message into meaningful components.

    The results are as follows:

        error
        method
        url
        version
        headers
        body

    See http://stackoverflow.com/questions/2115410/does-python-have-a-module-for-parsing-http-requests-and-responses
    """
    def __init__(self, request):
        metadata, data = request.split('\r\n\r\n', 1)
        self.rfile = StringIO(metadata)
        self.raw_requestline = self.rfile.readline()
        self.error = ()
        self.parse_request()

        # Note: values on the right side are generated
        #       in BaseHTTPRequestHandler::parse_request()
        if not self.error:
            self.method = self.command
            self.url = self.path
            self.version = self.request_version
            self.headers = {name: self.headers[name] for name in self.headers}
            self.body = data

    def send_error(self, code, message):
        self.error = (code, message)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
