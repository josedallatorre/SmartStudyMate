import ast
import asyncio
import json
import os
import threading
import time
import aiohttp
import Converter
import Converter
from pathlib import Path
from pathlib import Path
from flask import Flask, jsonify,  request
app = Flask(__name__,
            static_url_path='',
            static_folder='static')
# needed if the app is behind a proxy
#from werkzeug.middleware.proxy_fix import ProxyFix
#app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Store for generated files and their progress
download_progress = {}

# used to check if the app is up
@app.route('/')
def hello_world():
    return 'Hello, World!'

# route that receives the selected files and starts the download
@app.route("/handle_data/<file_id>", methods=['POST'])
def handle_data(file_id):
    selected_contents = request.get_json()
    user = selected_contents[-2]
    team_name = selected_contents[-1]
    user1 = [ast.literal_eval(item) for item in user]
    team = [ast.literal_eval(item) for item in team_name]
    # Extract the dictionary from the list
    if isinstance(user1, list) and len(user1) == 1 and isinstance(user1[0], dict):
        data_dict = user1[0]
    else:
        print("Data is not in the expected format.")
    if isinstance(team, list) and len(team) == 1 and isinstance(team[0], dict):
        team_dict = team[0]
    else:
        print("Data is not in the expected format.")
    user_email = data_dict['mail']
    team_string_name = team_dict['team_name']
    # Remove the last two elements from the list
    selected_contents.pop()
    selected_contents.pop()
    my_list = [ast.literal_eval(item) for item in selected_contents]
    for content in my_list:
        download_progress[content['id']] = 0  # Initialize progress
        threading.Thread(target=start_download, args=(content,)).start()
    # Start a background thread to monitor when all downloads are done
    threading.Thread(target=monitor_completion,args=(my_list,user_email,team_name)).start()
    return selected_contents

def monitor_completion(my_list,user_email,team_name):
    # This function will keep checking if all downloads are complete
    while not all(progress == 100 for progress in download_progress.values()):
        time.sleep(1)  # Sleep for a bit to avoid busy waiting
    paths = []
    for content in my_list:
        filename = content['id'] + ".mp4"
        paths.append(Path(filename))

    # Once all downloads are complete, call 
    Converter.useConverter(paths,team_name,user_email)

def start_download(content):
    asyncio.run(download_file(content))

async def download_file(content):
    print(content)
    filename = content['id'] + ".mp4"
    path = os.path.join('static',filename)
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
                        """
                          after the download is done we convert the file 
                          from mp4 to mp3
                        """
            except asyncio.TimeoutError:
                print(f"timeout error on {content['@microsoft.graph.downloadUrl']}")

# function to update the progress of the download
def update_progress(content_id, progress):
    if content_id in download_progress:
        download_progress[content_id] = progress
        print(f"Progress for file {content_id}: {progress}%")

# route to get the progress of the download
@app.route('/progress_status/<file_id>')
def progress_status(file_id):
    # Calculate overall progress
    total_progress = sum(download_progress.values())
    overall_progress = total_progress / len(download_progress) if download_progress else 100
    print(overall_progress)
    return jsonify(progress=overall_progress)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)