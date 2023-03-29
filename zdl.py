import os
from flask import Flask, abort, request, send_file
from uuid import uuid4
import requests
import requests.auth
import urllib

CLIENT_ID = "gs1Vw45Tre38B9a2W5Yjg"
CLIENT_SECRET = "lG6YYbw1Wit2kwOfeENRY4dPgY1DhmS5"
REDIRECT_URI = "http://localhost:65010/zoom_callback"

app = Flask(__name__)

@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with Zoom</a>'
    return text % make_authorization_url()

def make_authorization_url():
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "redirect_uri": REDIRECT_URI}
    url = "https://zoom.us/oauth/authorize?" + urllib.parse.urlencode(params)
    return url

@app.route('/zoom_callback')
def zoom_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error

    code = request.args.get('code')
    access_token = get_token(code)

    # Download recording
    meeting_id = '0'
    from_date = '2023-03-01'
    recording_url = get_recording_url(access_token, meeting_id, from_date)
    recording_file = os.path.join('D:/recordings', f'{meeting_id}.mp4')
    r = requests.get(recording_url, stream=True)
    with open(recording_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return send_file(recording_file, as_attachment=True)

def get_recording_url(access_token, meeting_id, from_date):
    headers = {"Authorization": "Bearer " + access_token}
    url = f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings?from={from_date}"
    response = requests.get(url, headers=headers)
    recording_json = response.json()
    recording_files = recording_json["recording_files"]
    print("recording_files:", recording_files)
    download_url = recording_files[0]["download_url"]
    print("download_url:", download_url)
    return download_url

def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}

    response = requests.post("https://zoom.us/oauth/token",
                             auth=client_auth,
                             data=post_data)
    token_json = response.json()
    print(token_json)
    return token_json["access_token"]

if __name__ == '__main__':
    app.run(debug=True, port=65010)
