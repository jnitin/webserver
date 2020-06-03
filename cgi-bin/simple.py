#!/user/bin/evn python3.8.3

from datetime import datetime
import cgitb

cgitb.enable()    # Allows for debugging errors from the cgi scripts in the browser

print('''\
<html>
<body>
<p>Generated {0}</p>
</body>
</html>'''.format(datetime.now()))
