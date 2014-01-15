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
    print req.path_qs.lstrip("http://").lstrip(req.host)
    i_headers = {}
    for tmp in req.headers:
        i_headers[tmp] = req.headers[tmp]
    st = req.path_qs
    conn.request(req.method, req.path_qs.lstrip("http://").lstrip(req.host), body = req.body, headers = i_headers)
    #conn.request(req.method, "http://www.baidu.com/", body = req.body, headers = i_headers)
    r1 = conn.getresponse()
    resp = Response(request = req)
    #fp = open("./tmp.html", "w+")
    while True:
        body = r1.read(65536)
        if not body:
            resp.body_file.write("%x\r\n\r\n"%(0))
            #fp.write("%x\r\n\r\n" % (0))
            break
        resp.body_file.write("%x\r\n%s\r\n" % (len(body),body))
        #fp.write("%x\r\n%s\r\n" % (len(body),body))
    #fp.close()
    resp.status = r1.status
    for tmp in r1.getheaders():
        resp.headers.add(tmp[0], tmp[1])
    #conn.close()
    return resp
    
socket = eventlet.listen(('0.0.0.0', 12345))
#wsgi_kwargs = {'func':wsgi.server, 'site':hello_world, 'sock':socket, 'custom_pool':eventlet.GreenPool(1000)}
#server = eventlet.spawn(**wsgi_kwargs)
#server.wait()
wsgi.server(socket, hello_world, custom_pool = eventlet.GreenPool(1000))
