# -*- coding: utf-8 -*-
from eventlet import wsgi, api
import eventlet
import webob.dec
from webob import Request, Response
from StringIO import StringIO
from pprint import pprint
import httplib



@webob.dec.wsgify(RequestClass=Request)
def hello_world(req):
    conn = httplib.HTTPConnection(req.host)
    #conn = httplib.HTTPConnection("www.baidu.com")
    print req.host
    print req.path_qs
    i_headers = {}
    for tmp in req.headers:
        i_headers[tmp] = req.headers[tmp]
    st = req.path_qs
    conn.request(req.method, req.path_qs.lstrip("http://").lstrip(req.host), body = req.body, headers = i_headers)
    #conn.request(req.method, "http://www.baidu.com/", body = req.body, headers = i_headers)
    r1 = conn.getresponse()
    resp = Response()
    resp.status = r1.status
    for tmp in r1.getheaders():
        if tmp[0] == "content-type":
            resp.content_type = tmp[1]
        elif tmp[0] == "content-length":
            resp.content_length = tmp[1]
        else:
            resp.headers.add(tmp[0], tmp[1])
    if resp.headers.get("transfer-encoding", None) == "chunked":
        read_body(r1, resp.body_file)
    else:
        resp.body = r1.read()
    conn.close()
    return resp
    
def read_body(fread, fwrite):
    while True:
        body = fread.read(32768)
        if not body:
            fwrite.write("%x\r\n\r\n" % (0))
            break
        fwrite.write("%x\r\n%s\r\n" % (len(body),body))

socket = eventlet.listen(('0.0.0.0', 12345))
#wsgi_kwargs = {'func':wsgi.server, 'site':hello_world, 'sock':socket, 'custom_pool':eventlet.GreenPool(1000)}
#server = eventlet.spawn(**wsgi_kwargs)
#server.wait()
wsgi.server(socket, hello_world, custom_pool = eventlet.GreenPool(1000))
