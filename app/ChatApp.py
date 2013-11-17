#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['ChatApp']

class MetaChatApp(type):
    """The metaclass of ChatApp.
    """
    def __new__(cls, name, bases, dict):
        dict['route'] = []
        return super(MetaChatApp, cls).__new__(cls, name, bases, dict)

class ChatApp:
    """The base class of all applications in Chat System.

        >>> from ChatApp import ChatApp
        >>> class TestApp(ChatApp):
        ...     @classmethod
        ...     def POST(cls):
        ...         return (404, {}, '')
        ...
        >>> apps = [('/test', TestApp),]
        >>> ChatApp.mount(apps)
        >>> ChatApp.GET({})
        (200, {'Content-Type': 'text/html; charset=en', 'Server': 'ChatSystem'}, '<a href="/test">TestApp</a>')
    """
    ##### Each subclass of ChatApp get one more class-level attribute:
    #
    # route strategy
    #
    # route = [
    #     (pattern, subapp),
    # ]
    #
    # if `pattern` matches, then `subapp` is selected to response.
    #
    __metaclass__ = MetaChatApp

    @classmethod
    def mount(cls, apps):
        """Mount `apps` as subapps with patterns.
        """
        import collections
        assert isinstance(apps, collections.Iterable), \
               '`apps` must be iterable'
        for pattern, subapp in apps:
            assert isinstance(pattern, basestring), \
                   '`pattern` must a be string'
            assert issubclass(subapp, ChatApp) and subapp is not ChatApp, \
                   '`subapp` must be a proper subclass of ChatApp'
            cls.route.append((pattern, subapp))

    @classmethod
    def delegate(cls, environ, handler, error_handler):
        path, command = environ['PATH_INFO'], environ['REQUEST_METHOD']

        if not path or path == '/': # `cls` is the target app
            # get method
            method = getattr(cls, command, None)
            if not method:
                error_handler(501, "Unsupported method (%r)" % command)
                return
            # call `handler`
            status_code, headers, entity_body = method(environ)
            handler(status_code, headers, entity_body)
        else: # `cls` is a mediate app
            import re
            for pattern, app in cls.route:
                m = re.match(pattern, path)
                if m: # `pattern` matches
                    environ['PATH_INFO'] = path[len(m.group(0)):] # home path for `app`
                    app.delegate(environ, handler, error_handler)
                    break
            else:
                error_handler(404, "No application registered matches (%r)" % path)

    @classmethod
    def GET(cls, env):
        if cls.route:
            entity_body = '\n'.join('<a href="%s">%s</a>' % (pattern, subapp.__name__)
                                    for pattern, subapp in cls.route)
        else:
            entity_body = 'Welcome!'
        return (200,
                {
                    'Content-Type': 'text/html; charset=en',
                    'Server': 'ChatSystem',
                },
                entity_body)

    @classmethod
    def HEAD(cls, env):
        return (200,
                {
                    'Content-Type': 'text/html; charset=en',
                    'Server': 'ChatSystem',
                },
                '')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
