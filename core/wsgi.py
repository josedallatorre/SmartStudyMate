from app import app
import os

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get("GPU_SERVER_PORT"), debug=True)
