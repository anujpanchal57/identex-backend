import os
import sys

app_name = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/'))
sys.path.insert(0, app_name)

from functionality.main import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000')
