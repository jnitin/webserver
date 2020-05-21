#!/usr/bin/env python3.8.3

import cgi, cgitb
cgitb.enable()		## allows for debugging errors from the cgi scripts in the browser

form = cgi.FieldStorage()

print("Content-type:text/html\r\n\r\n")
print('<html>')
print('<head>')
print('<title>Hello World - First CGI Program</title>')
print('</head>')
print('<body>')
print('<h2>Hello World! This is my first CGI program</h2>')
print('</body>')
print('</html>')