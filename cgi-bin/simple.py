#!F:\Python\Pycharm_Program\venv\Scripts\python.exe
from datetime import datetime
import cgitb

cgitb.enable()

print('''\
<html>
<body>
<p>Generated {0}</p>
</body>
</html>'''.format(datetime.now()))
