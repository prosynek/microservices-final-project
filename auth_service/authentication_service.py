from flask import Flask, redirect, request, jsonify
import requests
from urllib.parse import urlencode
from config import CLIENT_ID, CLIENT_SECRET
import flask_monitoringdashboard as dashboard

app = Flask(__name__)
dashboard.config.init_from(file='auth_config.cfg')

PORT = 8000
REDIRECT_URI = 'http://146.190.166.177:5000/callback'             # redirect back to client on droplet HTTP://app_service:5000/callback
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SCOPE = 'user-library-read user-top-read user-read-recently-played user-read-private user-read-email' 

# Request new access token using refresh token
def get_access_token(payload):
    response = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# responsible for passing out access tokens
@app.route('/authorize')
def authorize():
    print('-------- AUTH AUTHORIZE --------')
    url_params = urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI # Redirect to client callback URL
    })

    auth_url = f'{SPOTIFY_AUTH_URL}?{url_params}'
    print(f'AUTH URL {auth_url}')

    return jsonify({'auth_url': auth_url})


@app.route('/token', methods=['POST'])
def token():
    payload = request.json
    grant_type = payload.get('grant_type')

    if grant_type == 'authorization_code':
        # Authorization code grant type
        payload['client_id'] = CLIENT_ID
        payload['client_secret'] = CLIENT_SECRET
        payload['redirect_uri'] = REDIRECT_URI

    elif grant_type == 'refresh_token':
        # Refresh token grant type
        payload['client_id'] = CLIENT_ID
        payload['client_secret'] = CLIENT_SECRET

    else:
        return jsonify({'error': 'Invalid grant type'}), 400

    response_data = get_access_token(payload)

    if response_data:
        return jsonify(response_data), 200
    else:
        return jsonify({'error': 'Failed to obtain access token'}), 400
    
dashboard.bind(app)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=PORT)
