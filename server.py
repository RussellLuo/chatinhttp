#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BaseHTTPServer

from app.ChatApp import ChatApp

__all__ = ['ChatHTTPServer']

class ChatHTTPServer(BaseHTTPServer.HTTPServer):
    """The server of Chat System.
    """
    @staticmethod
    def mount(apps):
        ChatHTTPRequestHandler.mount(apps)

    @classmethod
    def run(cls, host, port):
        try:
            server_address = (host, port)

            ChatHTTPRequestHandler.protocol_version = 'HTTP/1.0'
            httpd = cls(server_address, ChatHTTPRequestHandler)

            sa = httpd.socket.getsockname()
            print('http://{0}:{1}/'.format(*sa))
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

class ChatHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler, ChatApp):
    """The hanlder in ChatHTTPServer.
    """
    def handle_one_request(self):
        """Override to use a new strategy for method selection.
        """
        import socket
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return

            ##### Customization
            # origin
            """
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(501, "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            method()
            """
            # now
            #import pdb; pdb.set_trace()
            self.delegate(self.get_environ(), self.gen_response, self.send_error)

            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout, e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return

    def send_response(self, code, message=None):
        """Override to just send raw response without additional headers.
        """
        self.log_request(code)
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        if self.request_version != 'HTTP/0.9':
            self.wfile.write("%s %d %s\r\n" %
                             (self.protocol_version, code, message))
            # print (self.protocol_version, code, message)

        ##### Customization
        # origin
        """
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        """
        # now (no additional headers)

    def get_environ(self):
        """Get request message as environment information.
        """
        # REQUEST_METHOD
        environ = {'REQUEST_METHOD': self.command}

        # PATH_INFO and QUERY_STRING
        if '?' in self.path:
            path, qs = self.path.split('?', 1)
        else:
            path, qs = self.path, ''
        environ['PATH_INFO'] = path
        environ['QUERY_STRING'] = qs

        # headers
        for key in self.headers:
            environ[key.upper()] = self.headers[key]

        # entity data
        '''
        data_len = -1
        if 'Content_Length' in self.headers:
            try:
                data_len = int(self.headers['Content_Length'])
            except ValueError:
                pass
        try:
            environ['REQUEST_DATA'] = self.rfile.read(data_len)
        except Exception:
            environ['REQUEST_DATA'] = ''
        '''

        return environ

    def gen_response(self, status_code, headers, entity_body):
        """Generate response based on `status_code`, `headers` and `entity_body`.
        """
        # start line
        self.send_response(status_code)

        # headers
        for key in headers:
            self.send_header(key, headers[key])
        if headers:
            self.end_headers()

        # entity body
        if entity_body:
            self.wfile.write(entity_body)



if __name__ == '__main__':
    import sys
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8000

    from App.Authentication import Authentication
    ChatHTTPServer.mount(
        apps = (
            ('/auth', Authentication),
        )
    )

    ChatHTTPServer.run('', port)
