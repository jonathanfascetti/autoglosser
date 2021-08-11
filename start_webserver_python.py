#!/usr/bin/env python3
# coding: utf-8


import http.server
import cgitb
import os
import sys


cgitb.enable()  # enable CGI error reporting

PATH = "./site/"
PORT = 9000
server_address = ("", PORT)

web_dir = PATH
# web_dir = os.path.join(os.path.dirname(__file__), 'site')
# web_dir = os.path.join(PATH, "htdocs")
os.chdir(web_dir)

server = http.server.HTTPServer
handler = http.server.CGIHTTPRequestHandler
handler.cgi_directories = ["/cgi-bin"]

httpd = server(server_address, handler)

try:
    print("Serving %s at port %s..." % (PATH, PORT))
    httpd.serve_forever()

except KeyboardInterrupt:
    print("\nKeyboard interrupt received, exiting.")
    sys.exit(0)
