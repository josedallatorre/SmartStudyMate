from flask import Flask,  request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/handle_data", methods=['POST'])
def handle_data():
    selected_contents = request.get_json()
    print("ciao",selected_contents)
    file_id = str(time.time())  # Simple unique ID for the download session
    return selected_contents

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
