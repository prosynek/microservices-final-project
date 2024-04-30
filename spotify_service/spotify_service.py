from flask import Flask, request, jsonify
import requests
import flask_monitoringdashboard as dashboard

app = Flask(__name__)
dashboard.config.init_from(file='spotify_config.cfg')

PORT = 8080
SPOTIFY_BASE_URL = 'https://api.spotify.com/v1'

def validate_request(auth_header):
    """
    Checks if the request header contains a valid access token.

    :param auth_header: authorization header of the request
    :returns: valid authorization header to be used in request
    """
    if not auth_header:
        return jsonify({'error' : 'No access token found.'}), 400
    
    access_token = auth_header.split(' ')[1]
    request_header = {'Authorization' : f'Bearer {access_token}'}
    return request_header


@app.route('/user', methods=['GET'])
def user():
    headers = validate_request(request.headers.get('Authorization')) 
    response = requests.get(f'{SPOTIFY_BASE_URL}/me', headers=headers)

    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'error' : 'Failed to fetch spotify user data.'}), response.status_code
    

@app.route('/user/top', methods=['GET']) 
def top():
    headers = validate_request(request.headers.get('Authorization')) 

    # parse request params
    term = request.args.get('term')
    item_type = request.args.get('type')

    # if params are valid, make request - gets top 10 tracks or artists depending on type
    if (term in ['short_term', 'medium_term', 'long_term']) and (item_type in ['tracks', 'artists']):
        payload = {'time_range' : term, 'limit' : 10}
        response = requests.get(f'{SPOTIFY_BASE_URL}/me/top/{item_type}', headers=headers, params=payload)
    else:
        return jsonify({'error' : 'Invalid parameters. Valid term values: [short, medium, long]. Valid type values: [artists, tracks]'})
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'error' : 'Failed to fetch spotify user data.'}), response.status_code

dashboard.bind(app) # for monitoring dashboard

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=PORT)