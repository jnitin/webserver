#!/user/bin/evn python3.8.3

import cgi, cgitb
cgitb.enable()

form = cgi.FieldStorage()

# getting the data from the fields
username = form.getvalue('username')
password = form.getvalue('password')
if password is None:
    username = 'user'
    password = '123'

print("Content-type:text/html\r\n\r\n")
print("<html>")
print("<head><title>User entered</title></head>")
print("<body>")
print("<h1>User has entered</h1>")
print("<b>Username : </b>", username, "<br>")
print("<b>Password : </b>", password, "<br>")
print("")
print("</div>")
print("</body>")
print("</html>")