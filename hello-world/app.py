import ast
import asyncio
import json
import os
import threading
import time
import aiohttp
from flask import Flask, jsonify,  request
app = Flask(__name__)

# Store for generated files and their progress
download_progress = {}

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/handle_data/<file_id>", methods=['POST'])
def handle_data(file_id):
    selected_contents = request.get_json()
    my_list = [ast.literal_eval(item) for item in selected_contents]
    print(file_id)
    file_id = str(time.time())  # Simple unique ID for the download session
    for content in my_list:
        print("ciao122",content,type(content))
        download_progress[content['id']] = 0  # Initialize progress
        threading.Thread(target=start_download, args=(file_id,content,)).start()
    return selected_contents

def start_download(file_id,content):
    asyncio.run(download_file(content))

async def download_file(content):
    print(content)
    filename = content['id'] + ".mp4"
    #path = os.path.join('static',filename)
    path = filename
    # Check whether the specified file exists or not 
    if(os.path.exists(path)):
        print('file already exists, skippping: ',filename)
        update_progress(content['id'], 100)
    else:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(content['@microsoft.graph.downloadUrl']) as response:
                    if response.status != 200:
                        resp ={"error": f"server returned {response.status}"}
                    else:
                        total_size = int(response.headers.get('Content-Length', 0))
                        chunk_size = 1024 * 1024  # 1MB
                        downloaded_size = 0
                        print(filename)
                        with open(path, mode="wb") as file:
                            async for chunk in response.content.iter_chunked(chunk_size):
                                if chunk:
                                    file.write(chunk)
                                    downloaded_size += len(chunk)
                                    progress = (downloaded_size / total_size) * 100
                                    update_progress(content['id'], progress)
                        update_progress(content['id'], 100)
                        print(f"Downloaded file {content['name']}")
            except asyncio.TimeoutError:
                print(f"timeout error on {content['@microsoft.graph.downloadUrl']}")

def update_progress(content_id, progress):
    print(download_progress)
    if content_id in download_progress:
        download_progress[content_id] = progress
        print(f"Progress for file {content_id}: {progress}%")

@app.route('/progress_status/<file_id>')
def progress_status(file_id):
    # Calculate overall progress
    total_progress = sum(download_progress.values())
    overall_progress = total_progress / len(download_progress) if download_progress else 100
    print(overall_progress)
    return jsonify(progress=overall_progress)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
