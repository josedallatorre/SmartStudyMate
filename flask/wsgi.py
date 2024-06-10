from app import app
import os
from werkzeug.middleware.proxy_fix import ProxyFix


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT"), debug=True)
