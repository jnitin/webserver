#!/user/bin/evn python3.8.3

import cgi, os
import cgitb; cgitb.enable()

form = cgi.FieldStorage()

# Get filename
fileitem = form['filename']

# Test if file uploaded
if fileitem.filename:
    message = 'ok'   
else:
    message = 'No file was uploaded'


print("Content-type: text/html")
print("")
print("""
<html>
<body>
  <p> %s </p
</body>
</html>
""" % message)