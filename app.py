from flask import Flask

app = Flask(__name__)

app.secret_key = "minify_inventory_2026"

from routes.auth import *
from routes.dashboard import *

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
    
