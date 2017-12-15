"""
    This program checks for new version of `app.py`
    and downloads it if it's needed
"""

import hashlib
from urllib.request import urlopen

FILE_UPDATE_URL = 'http://dev.jozefcipa.com/spse-switch/app.py'

# Calculate hash from local file
app_file = open('app.py', 'rb').read()
current_file_md5 = hashlib.md5(app_file).hexdigest()

# Calculate hash from remote file
remote_file = urlopen(FILE_UPDATE_URL).read()
remote_file_md5 = hashlib.md5(remote_file).hexdigest()

# Check if there is a difference between files
if remote_file_md5 is not current_file_md5:

    # Download new file
    with open('app.py', "wb") as updated_file:
        updated_file.write(remote_file)
