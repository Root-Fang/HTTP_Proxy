# -*- coding: utf-8 -*-

default_host = "127.0.0.1"
default_port = 12345

def bool_check(value):
    if value in [False, "F", "f", 0, "0", "NO", "no", "No"]:
        return False
    else:
        return True

class server(object):
    def __init__(self, host, port, worker, use_ssl, **kwarg):
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
        self.kwarg = kwarg
    @classmethod
    def create(cls, conf):
        pass
