#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ChatApp

__all__ = ['Authentication']

class Authentication(ChatApp.ChatApp):
    pass

class BasicAuthentication(ChatApp.ChatApp):
    """Application of basic authentication.
    """
    @classmethod
    def GET(cls, env):
        if 'Authorization'.upper() not in env:
            return (401,
                    {
                        'Content-Type': 'text/html; charset=en',
                        'Server': 'AuthApp',
                        'WWW-Authenticate': 'Basic realm="Family"',
                    },
                    '')
        else:
            return (200,
                    {
                        'Content-Type': 'text/html; charset=en',
                        'Server': 'AuthApp',
                    },
                    'Basic Authentication')

Authentication.mount(
    apps = (
        ('/basic', BasicAuthentication),
    )
)
