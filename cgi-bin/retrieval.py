#!/usr/bin/env python3.8.3

import cgi, cgitb
cgitb.enable()		## allows for debugging errors from the cgi scripts in the browser

form = cgi.FieldStorage()

## getting the data from the fields
first = form.getvalue('username')
last = form.getvalue('password')


print("Content-type:text/html\r\n\r\n")
print("<html>")
print("<head><title>User entered</title></head>")
print("<body>")
print("<h1>User has entered</h1>")
print("<b>Firstname : </b>" + first + "<br>")
print("<br><b>Lastname : </b>" + last + "<br>")
print("")
print("</div>")
print("</body>")
print("</html>")