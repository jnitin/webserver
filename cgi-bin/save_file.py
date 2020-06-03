"""This is save file module"""
import cgi
import cgitb

cgitb.enable()

form = cgi.FieldStorage()
fileItem = form['filename']

# Test if file uploaded
if fileItem.filename:
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
