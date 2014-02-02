# -*- coding: utf-8 -*-
from eventlet import wsgi, api
import eventlet
import webob.dec
from webob import Request, Response
from multiprocessing import cpu_count
from StringIO import StringIO
import httplib
import socket
import traceback

class proxy(object):
    
    chunk_length = 32768
    
    def __init__(self, time_out = None, logger = None, **kwarg):
        super(proxy, self).__init__()
        self.time_out = time_out
        self.logger = logger
    def read_chunk_body(self, fread, fwrite):
        while True:
            body = fread.read(self.chunk_length)
            if not body:
                fwrite.write("%x\r\n\r\n" % (0))
                break
            fwrite.write("%x\r\n%s\r\n" % (len(body),body))
            
    def handshake(self, req, socks):
        host = req.path_info.split(":")[0]
        port = int(req.path_info.split(":")[1])
        server = eventlet.connect((host, port))
        
        client = req.environ['eventlet.input'].get_socket()
        client.sendall("HTTP/1.1 200 OK\r\n\r\n")
        socks['client'] = client
        socks['server'] = server
        
        
    def one_way_proxy(self, source, dest):
        """Proxy tcp connection from source to dest."""
        while True:
            try:
                d = source.recv(32768)
            except Exception:
                d = None

            if d is None or len(d) == 0:
                #dest.shutdown(socket.SHUT_WR)
                dest.close()
                break
            try:
                dest.sendall(d)
            except Exception:
                source.close()
                dest.close()
                break
    @webob.dec.wsgify
    def __call__(self, req):
#        url = None
#        ret = None
#        conn = None
#        body = None
        try:
            if req.method == "CONNECT":
                socks = {}
                t0 = self.pool.spawn(self.handshake, req, socks)
                t0.wait()
                client = socks['client']
                server = socks['server']
                t1 = self.pool.spawn(self.one_way_proxy, client, server)
                t2 = self.pool.spawn(self.one_way_proxy, server, client)
                t1.wait()
                t2.wait()
                
                client.close()
                server.close()
                return
            else:
                host = req.host
                port = int(req.host_port)
                server = eventlet.connect((host, port))
                client = req.environ['eventlet.input'].get_socket()
                
                url = req.path_qs.lstrip("http://").lstrip(req.host)
                server.sendall("%s %s %s\r\n" % (req.method, url, req.http_version))
                for tmp in req.headers:
                    server.sendall("%s:%s\r\n" % (tmp, req.headers[tmp]))
                server.sendall("\r\n")
                if req.content_length != 0 or req.content_length != None:
                    body = ""
                    if req.headers.get("transfer-encoding", None) == "chunk" and req.is_body_readable:
                        rtmp = req.body_file_seekable
                        wtmp = StringIO()
                        self.read_chunk_body(rtmp, wtmp)
                        body = wtmp.read()
                    else:
                        body = req.body
                    server.sendall(body)
                
                t = self.pool.spawn(self.one_way_proxy, server, client)
                t.wait()
                
                server.close()
                client.close()
                return
        except Exception, e:
            sock = req.environ['eventlet.input'].get_socket()
            sock.close()
#        try:
#            conn = httplib.HTTPConnection(req.host, timeout = self.time_out)
#            url = req.path_qs.lstrip("http://").lstrip(req.host)
#        except Exception, e:
#            conn.close()
#            return
#            
#        i_headers = {}
#        for tmp in req.headers:
#            i_headers[tmp] = req.headers[tmp]
#        
#        if req.is_body_readable:
#            body = req.body_file_seekable
#        else:
#            body = req.body
#        
#        try:
#            conn.request(req.method, url, body = body, headers = i_headers)
#            ret = conn.getresponse()
#        except Exception, e:
#            #conn.close()
#            return 
#        
#        resp = Response()
#        resp.status = ret.status
#        for tmp in ret.getheaders():
#            if tmp[0] == "content-type":
#                resp.content_type = tmp[1]
#            elif tmp[0] == "content-length":
#                resp.content_length = tmp[1]
#            else:
#                resp.headers.add(tmp[0], tmp[1])
#        if resp.headers.get("transfer-encoding", None) == "chunked":
#            self.read_chunk_body(ret, resp.body_file)
#        else:
#            resp.body = ret.read()
#        conn.close()
#        return resp
        
    @classmethod
    def factory(cls, global_conf, **local_conf):
        local_conf.update(global_conf)
        return cls(**local_conf)


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

if(proxy.pool == None):
    proxy.pool = eventlet.GreenPool(1000)


sock = eventlet.listen(('0.0.0.0', 12345))
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
#wsgi_kwargs = {'func':wsgi.server, 'site':hello_world, 'sock':socket, 'custom_pool':eventlet.GreenPool(1000)}
#server = eventlet.spawn(**wsgi_kwargs)
#server.wait()
try:
    wsgi.server(sock, proxy.factory({}), protocol=SafeHttpProtocol, custom_pool = proxy.pool, keepalive = False)
except Exception:
    traceback.print_exc()
