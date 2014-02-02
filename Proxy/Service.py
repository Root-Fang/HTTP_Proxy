# -*- coding: utf-8 -*-
import os
from proxy_exceptions import *

default_host = "127.0.0.1"
default_port = 12345

def bool_check(value):
    if value in [False, "F", "f", 0, "0", "NO", "no", "No"]:
        return False
    else:
        return True

class Server(object):
    def __init__(self, app_name, host, port, worker, use_ssl, pool_size, **kwarg):
        if app_name is None:
            self.app_name = "main"
        else:
            self.app_name = app_name
        if host is None:
            self.host = default_host
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
    @classmethod
    def create(cls, conf):
        if conf is None:
            conf = "../etc/proxy.conf"
            if not os.path.exists(conf):
                raise FileException(conf)
        else:
            if not os.path.exists(conf):
                raise FileException(conf)
    def start(self):
        pass
    def wait(self):
        pass
    def stop(self):
        pass


class Lancher(object):
    def __init__(self, server):
        self.server = server
    def start(self):
        self.server.start()
    def wait(self):
        self.server.wait()
    def stop(self):
        sef.server.stop()
