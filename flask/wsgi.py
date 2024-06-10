from app import app
import os
from werkzeug.middleware.proxy_fix import ProxyFix


if __name__ == "__main__":
    app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT"), debug=True)
