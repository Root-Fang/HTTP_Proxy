# -*- coding: utf-8 -*-
import os
from config import CONF
from proxy_exceptions import *
from eventlet import wsgi
from paste import deploy
import eventlet
from eventlet import wsgi
import socket
import traceback
import threading
import sys

default_port = 12345

def bool_check(value):
    if value in [False, "F", "f", 0, "0", "NO", "no", "No"]:
        return False
    else:
        return True

class Server(object):
    def __init__(self, app_path = None, app_name = None, host = None, port = None, worker = None, use_ssl = None, pool_size = None, **kwarg):
        if app_path is None:
            self.app_path = "proxy.conf"
        else:
            self.app_path = app_path
        self.app_path = os.path.abspath("../etc/" + app_path)
        if not os.path.exists(self.app_path):
            raise FileException(self.app_path)
        if app_name is None:
            self.app_name = "main"
        else:
            self.app_name = app_name
        if host is None:
            self.host = socket.gethostbyname(socket.gethostname())
        else:
            self.host = host
        if port is None:
            self.port = default_port
        else:
            self.port = port
        if worker is None:
            self.worker = cpu_count()
        else:
            self.worker = worker
        if use_ssl is None:
            self.use_ssl = False
        else:
            self.use_ssl = bool_check(use_ssl)
        if pool_size is None:
            self.pool_size = 1000
        else:
            self.pool_size = pool_size
        self.kwarg = kwarg
        try:
            self.app = deploy.loadapp("config:%s" % self.app_path, name = self.app_name)
        except Exception, e:
            raise e
        self.sock = eventlet.listen((self.host, self.port))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._server = []
        self._pool = []
    @classmethod
    def create(cls, conf = None):
        if conf is None:
            conf = "../etc/proxy.ini"
            if not os.path.exists(conf):
                raise FileException(conf)
        else:
            if not os.path.exists(conf):
                raise FileException(conf)
        data = CONF(conf)
        return Server(app_path = data['app_path'], app_name = data['app_name'], host = data['host'], \
                    port = int(data['port']), worker = int(data['worker']), use_ssl = data['use_ssl'], \
                    pool_size = int(data['pool_size']))
    def start(self):
        pool = eventlet.GreenPool(self.pool_size)
        self._pool.append(pool)
        wsgi_kwargs = {
            'func': eventlet.wsgi.server,
            'sock': self.sock,
            'site': self.app,
            'protocol': SafeHttpProtocol,
            'custom_pool': pool,
            'keepalive': False, 
            }
        
        try:
            server = eventlet.spawn(**wsgi_kwargs)
            self._server.append(server)
            server.wait()
        except Exception:
            traceback.print_exc()
    def stop(self):
        for (num, server) in enumerate(self._server):
            self._pool[num].resize(0)
            server.kill()


class Lancher(object):
    def __init__(self, server = None):
        if server is None:
            raise ParaNotProvide(self.__class__.__name__)
        self.server = server
        self.count = server.worker
        self.child = []
    def _child_process(self):
        eventlet.hubs.use_hub()
        self.server.start()
        self.server.wait()
    def start(self):
        for num in range(self.count):
            thread = threading.Thread(target = self._child_process)
            thread.start()
            self.child.append(thread)
    def wait(self):
        for thread in self.child:
            thread.join()
        print "Run Over"
    def stop(self):
        sef.server.stop()

class SafeHttpProtocol(eventlet.wsgi.HttpProtocol):
    """HttpProtocol wrapper to suppress IOErrors.

       The proxy code above always shuts down client connections, so we catch
       the IOError that raises when the SocketServer tries to flush the
       connection.
    """
    def finish(self):
        try:
            eventlet.green.BaseHTTPServer.BaseHTTPRequestHandler.finish(self)
        except IOError:
            pass
        eventlet.greenio.shutdown_safe(self.connection)
        self.connection.close()
