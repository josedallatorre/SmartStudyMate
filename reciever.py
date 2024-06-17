from flask import Flask, request

app = Flask(__name__)

@app.route('/receive', methods=['POST'])
def receive_file():
    data = request.get_json()
    with open('/data/received.json', 'w') as f:
        f.write(str(data))
    return 'File received', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
