import os
import identity.web
import requests
import threading
import time
import html
from flask import Flask, json, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_bootstrap import Bootstrap
import app_config
from PIL import Image, ImageDraw, ImageFont


__version__ = "0.8.0"  # The version of this sample, for troubleshooting purpose


app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

#otherwise it creates a flask_session dir and make conflict with Flask_session module
app.config["SESSION_FILE_DIR"] = "./flask_session_cache"
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

# necessary to check if the app is working
@app.route('/flask-health-check')
def flask_health_check():
	return "success"

# login route to authenticate the user
# all not authenticated users will be redirected to this route
@app.route("/login")
def login():
    return render_template("login.html", version=__version__, **auth.log_in(
        scopes=app_config.SCOPE, # Have user consent to scopes during log-in
        redirect_uri=url_for("auth_response", _external=True), # Optional. If present, this absolute URL must match your app's redirect_uri registered in Azure Portal
        #prompt="select_account",  # Optional. More values defined in  https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        ))

# route to handle the response from the authentication
@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))

# route to log out the user
@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))

# route to display the index page
# only authenticated users can access this route
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
    # if the users setted a photo, it will be saved in the static directory
    if photo:
        filename =session.get('user')['id']+".png"
        with open(os.path.join('static',filename), 'wb') as f:
            for chunk in photo.iter_content(1024):
                f.write(chunk)
        print('photo found')
    # otherwise, a default avatar will be created based on the user's name
    else:
        name = me['displayName']
        icon = create_avatar_with_initials(name)
        filename = os.path.join('static', me['id'] + ".png")  # Save in static directory
        print(filename)
        icon.save(filename)
    return render_template('index.html', user=session['user'], version=__version__)

# function to create an avatar based on the user's name
def create_avatar_with_initials(name, size=30, background_color=(240, 240, 240), text_color=(100, 100, 100)):
    initials = ''.join([part[0].upper() for part in name.split()][:2])
    # Create a blank image
    image = Image.new('RGB', (size, size), background_color)
    
    # Initialize the drawing context
    draw = ImageDraw.Draw(image)
    
    # Choose a font (adjust the path to a font file on your system)
    try:
        font = ImageFont.truetype("arial.ttf", size=int(size/2))
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text size and position
    text_width, text_height = draw.textsize(initials, font=font)
    text_x = (size - text_width) / 2
    text_y = (size - text_height) / 2
    
    # Draw the text on the image
    draw.text((text_x, text_y), initials, fill=text_color, font=font)
    
    return image


 
# route to display the about page
@app.route("/about")
def about():
    return render_template('about.html', user=session['user'])

# route to display a page with the result of the call to the downstream api
# the api it's predefined in config file: app_config.ENDPOINT
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

# route to display the teams page,
# where the user can see the teams he is part of
@app.route("/teams")
def teams():
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        "https://graph.microsoft.com/v1.0/me/joinedTeams?$select=id,displayName",
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    # download the profile picture of each team
    teams_photos =[]
    threads=[]
    # use use threads to download the profile picture of each team
    for team in api_result['value']:
        t1 = threading.Thread(target=download_propic, args=(team, token['access_token']))
        threads.append(t1)
    # call the start method of each thread
    for t in threads:
        t.start()
    # wait for all threads to finish
    for t in threads:
        t.join()
    # then render the teams page
    return render_template('teams.html', user=session.get('user'), teams=api_result['value'], img_data=teams_photos)

# function to download the profile picture of a team
def download_propic(team, token):
        team_photo = requests.get(
            "https://graph.microsoft.com/v1.0/teams/"+team['id']+"/photo/$value",
            headers={'Authorization': 'Bearer ' + token},
            timeout=30,
        )
        # check if the file already exists
        if(os.path.exists("static/"+team['id']+".jpg")):
            print('file already exists, skippping image of : ',team['id'])
        else:
            # otherwise, download the file
            with open("static/"+team['id']+".jpg", 'wb') as f:
                for chunk in team_photo.iter_content(1024):
                    f.write(chunk)

# route to display the channels of a team
@app.route("/<string:team_name>/drive/<string:team_id>")
def drive(team_id,team_name):
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        "https://graph.microsoft.com/v1.0/groups/"+team_id+"/drive/root/children",
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('drive.html', user=session.get('user'),
                           group_id= team_id,drive=api_result['value'],
                           team_name=team_name
                           )

# route to display the children of a folder, it could be a list of files or other folders
@app.route("/<string:team_name>/drive/<string:group_id>/drive_item_id/<string:drive_item_id>")
def drivechildrens(group_id,drive_item_id,team_name):
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    api_result = requests.get(
        "https://graph.microsoft.com/v1.0/groups/"+group_id+"/drive/items/"+drive_item_id+"/children",
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    print('api result:',api_result,'\n')
    return render_template('drive_children.html', user=session.get('user'), 
                           group_id=group_id, drive_children=api_result['value'],
                           team_name=team_name)

# route used to handle the data sent by the user from the form
# in drive_children page
@app.route("/handle_data", methods=['POST'])
def handle_data():
    selected_contents = request.form.getlist('selected_teams')
    team_name = request.form.getlist('team_name_json')
    user = request.form.getlist('user_json')
    # unescape the html entities
    user_unescaped = [html.unescape(item) for item in user]
    selected_contents.append(user_unescaped)
    selected_contents.append(team_name)
    # convert the list to a json object
    j = json.dumps(selected_contents)
    z = json.loads(j)
    file_id = str(time.time())  # Simple unique ID for the download session
    # retrieve the address and the port of the gpu server from .env file
    gpu_server =os.getenv("GPU_SERVER_ADDR")
    gpu_port =os.getenv("GPU_SERVER_PORT")
    # send the json object to the gpu server
    r = requests.post(f"http://{gpu_server}:{gpu_port}/handle_data/{file_id}", json=z)
    return jsonify({'file_id': file_id})


@app.route("/download/<file_id>")
def download(file_id):
    return render_template('download.html', user=session.get('user'),file_id=file_id)


@app.route('/progress_status/<file_id>')
def progress_status(file_id):
    # Calculate overall progress
    gpu_server =os.getenv("GPU_SERVER_ADDR")
    gpu_port =os.getenv("GPU_SERVER_PORT")
    overall_progress = requests.get(f"http://{gpu_server}:{gpu_port}/progress_status/{file_id}")
    print(overall_progress.json())
    return overall_progress.json()

if __name__ == "__main__":
    app.run(host="localhost",port=8000)