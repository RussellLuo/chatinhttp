#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Chat in HTTP protocol.

Usage:
    python ChatInHTTP.py [option] <host> [port]

option:
    -b    show entity body
    -i    show icons of client and server
"""

import sys
import os

from client import ChatHTTPClient
import icon

def chat(host, port, show_body, show_icon):
    session = ChatHTTPClient(host, port)
    try:
        while True:
            print(icon.client if show_icon else '[client]')
            req_msg = sys.stdin.read() # CTRL-D represents EOF
            req_msg = req_msg.replace(os.linesep, '\r\n')
            status, reason = session.request(req_msg)

            print(icon.server if show_icon else '[server]')
            if status:
                print(session.response(show_body))
            else:
                print(reason)
    except KeyboardInterrupt:
        pass

def getargs():
    import getopt

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'bi')

        optdict = dict(optlist)
        show_body = '-b' in optdict
        show_icon = '-i' in optdict

        if len(args) not in (1, 2):
            raise getopt.GetoptError('see usage')
        host = args[0]
        try:
            port = int(args[1])
        except (IndexError, ValueError):
            port = 80

        return (host, port, show_body, show_icon)
    except (getopt.GetoptError, ValueError):
        sys.stderr.write(__doc__)
        sys.exit(1)

if __name__ == '__main__':
    chat(*getargs())
