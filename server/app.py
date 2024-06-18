import os
import aiohttp
import identity.web
import requests
import ast
import threading
import asyncio
import time
from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_bootstrap import Bootstrap
import app_config
from content import Content
from PIL import Image
import base64
import io


__version__ = "0.8.0"  # The version of this sample, for troubleshooting purpose


app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')
app.config.from_object(app_config)
assert app.config["REDIRECT_PATH"] != "/", "REDIRECT_PATH must not be /"
Bootstrap(app)
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.jinja_env.globals.update(Auth=identity.web.Auth)  # Useful in template for B2C
auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)

# Store for generated files and their progress
download_progress = {}

@app.route("/login")
def login():
    return render_template("login.html", version=__version__, **auth.log_in(
        scopes=app_config.SCOPE, # Have user consent to scopes during log-in
        redirect_uri=url_for("auth_response", _external=True), # Optional. If present, this absolute URL must match your app's redirect_uri registered in Azure Portal
        #prompt="select_account",  # Optional. More values defined in  https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        ))


@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route("/")
def index():
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        # This check is not strictly necessary.
        # You can remove this check from your production code.
        return render_template('config_error.html')
    if not auth.get_user():
        return redirect(url_for("login"))
    token = auth.get_token_for_user(app_config.SCOPE)
    me = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    session['user'] = me
    photo = requests.get(
        "https://graph.microsoft.com/v1.0/me/photo/$value",
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    )
    if photo:
        with open(session.get('user')['id']+".jpg", 'wb') as f:
            for chunk in photo.iter_content(1024):
                f.write(chunk)
        print('photo found')
    return render_template('index.html', user=session['user'], version=__version__)


@app.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    api_result = requests.get(
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('display.html',user=session['user'], result=api_result)

@app.route("/teams")
def teams():
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        "https://graph.microsoft.com/v1.0/me/joinedTeams?$select=id,displayName",
        headers={'Authorization': 'Bearer ' + token['access_token']},
        #headers={'Authorization': 'Bearer ' + token.token},
        timeout=30,
    ).json()
    teams_photos =[]
    """
    for team in api_result['value']:
        team_photo = requests.get(
            "https://graph.microsoft.com/v1.0/teams/"+team['id']+"/photo/$value",
            headers={'Authorization': 'Bearer ' + token['access_token']},
            #headers={'Authorization': 'Bearer ' + token.token},
            timeout=30,
        )
        if(os.path.exists(team['id']+".jpg")):
            print('file already exists, skippping image of : ',team['id'])
        else:
            with open(team['id']+".jpg", 'wb') as f:
                for chunk in team_photo.iter_content(1024):
                    f.write(chunk)
        im = Image.open(team['id']+".jpg")
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())
        teams_photos.append(encoded_img_data.decode('utf-8'))
    """
    return render_template('teams.html', user=session.get('user'), teams=api_result['value'], img_data=teams_photos)

@app.route("/drive/<string:team_id>")
def drive(team_id):
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        "https://graph.microsoft.com/v1.0/groups/"+team_id+"/drive/root/children",
        headers={'Authorization': 'Bearer ' + token['access_token']},
        #headers={'Authorization': 'Bearer ' + token.token},
        timeout=30,
    ).json()
    return render_template('drive.html', user=session.get('user'),group_id= team_id,drive=api_result['value'])

@app.route("/drive/<string:group_id>/drive_item_id/<string:drive_item_id>")
def drivechildrens(group_id,drive_item_id):
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    api_result = requests.get(
        "https://graph.microsoft.com/v1.0/groups/"+group_id+"/drive/items/"+drive_item_id+"/children",
        headers={'Authorization': 'Bearer ' + token['access_token']},
        #headers={'Authorization': 'Bearer ' + token.token},
        timeout=30,
    ).json()
    print('api result:',api_result,'\n')
    return render_template('drive_children.html', user=session.get('user'), group_id=group_id, drive_children=api_result['value'])

@app.route("/handle_data", methods=['POST'])
def handle_data():
    selected_contents = request.form.getlist('selected_teams')
    my_list = [ast.literal_eval(item) for item in selected_contents]
    contents=[]
    for content in my_list:
        c = Content()
        c.url = content['@microsoft.graph.downloadUrl']
        c.name = content['name']
        c.id = content['id']
        contents.append(c)
        download_progress[c.id] = 0  # Initialize progress
        print("\n content:\n"+str(content)+"\n")
        print("\n c.url:\n"+str(c.url)+"\n")
        print("\n c.name:\n"+str(c.name)+"\n")
        print("\n c.id:\n"+str(c.id)+"\n")
    #file_ids = [str(time.time()) for _ in range(len(contents))] probably need it int the future
    file_id = str(time.time())  # Simple unique ID for the download session
    #for file_id, teams in zip(file_ids, contents):
    #start_time = time.time()    
    for content in contents:
        threading.Thread(target=start_download, args=(file_id,content,)).start()
    print('download done')
    #end_time = time.time()
    #elapsed_time = end_time - start_time
    #print("\nAll tasks completed in {:.2f} seconds".format(elapsed_time))
    #return render_template('download.html', result=contents)
    #return redirect(url_for('progress_page', file_id=file_id))
    return jsonify({'file_id': file_id})


@app.route('/progress/<file_id>')
def progress_page(file_id):
    return render_template('progress.html', file_id=file_id)

@app.route('/progress_status/<file_id>')
def progress_status(file_id):
    # Calculate overall progress
    total_progress = sum(download_progress.values())
    overall_progress = total_progress / len(download_progress) if download_progress else 100
    print(overall_progress)
    return jsonify(progress=overall_progress)

def start_download(file_id,content):
    asyncio.run(download_file(content))

async def download_file(content):
    # Specify path 
    filename = content.id + ".mp4"
    path = './' + filename
    # Check whether the specified 
    # path exists or not 
    if(os.path.exists(path)):
        print('file already exists, skippping: ',filename)
        update_progress(content.id, 100)
    else:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(content.url) as response:
                    if response.status != 200:
                        resp ={"error": f"server returned {response.status}"}
                    else:
                        total_size = int(response.headers.get('Content-Length', 0))
                        chunk_size = 1024 * 1024  # 1MB
                        downloaded_size = 0
                        filename = content.id + ".mp4"
                        print(filename)
                        with open(filename, mode="wb") as file:
                            async for chunk in response.content.iter_chunked(chunk_size):
                                if chunk:
                                    file.write(chunk)
                                    downloaded_size += len(chunk)
                                    progress = (downloaded_size / total_size) * 100
                                    update_progress(content.id, progress)
                        update_progress(content.id, 100)
                        print(f"Downloaded file {content.name}")
            except asyncio.TimeoutError:
                print(f"timeout error on {content.url}")



def update_progress(content_id, progress):
    if content_id in download_progress:
        download_progress[content_id] = progress
        print(f"Progress for file {content_id}: {progress}%")

if __name__ == "__main__":
    app.run(host="localhost")