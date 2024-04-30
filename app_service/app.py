from flask import Flask, redirect, request, jsonify, session, render_template
from collections import Counter
import requests
from datetime import datetime, timedelta, timezone
from database import MongoDBService
import flask_monitoringdashboard as dashboard


app = Flask(__name__)
app.secret_key = b'_dslkjh34@#Fsxr93DRG340[ppeo3-*d3&*(309'
dashboard.config.init_from(file='app_config.cfg')

AUTH_SERVICE = 'http://auth_service:8000'
SPOTIFY_SERVICE = 'http://spotify_service:8080'
DATABASE = 'spotify_db'


def store_token_data(token_data):
    """
    Stores spotify token data in session
    """
    expires_in = token_data.get('expires_in')
    expiry_time = datetime.now() + timedelta(seconds=expires_in)
    session['access_token'] = token_data.get('access_token')
    session['refresh_token'] = token_data.get('refresh_token')
    session['expires_at'] = expiry_time.astimezone(timezone.utc)


def refresh_access_token(refresh_token):
    """
    Makes request to authentication service to refresh spotify access token using refresh token
    """
    payload = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    response = requests.post(f'{AUTH_SERVICE}/token', json=payload)

    if response.status_code == 200:
        token_data = response.json()
        store_token_data(token_data)    # store token data in session
        return True
    return False


def get_sp_request_headers():
    """
    Retrieves spotify access token & constructs HTTP request header for requests to spotify service
    """
    access_token = session.get('access_token')
    expires_at = session.get('expires_at')
    refresh_token = session.get('refresh_token')

    # if access token missing, or expired, get new token
    if not access_token or not expires_at or expires_at <= datetime.now(timezone.utc):
        if refresh_token and refresh_access_token(refresh_token):
            access_token = session['access_token'] # token refreshed, update session data
        else:
            return jsonify({'error': 'Failed to obtain or refresh access token.'}), 401

    return {'Authorization': f'Bearer {access_token}'}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    response = requests.get(f'{AUTH_SERVICE}/authorize')
    auth_url = response.json().get('auth_url')
    if auth_url:
        return redirect(auth_url)
    else:
        return jsonify({'error': 'Failed to retrieve authorization URL from Spotify OAuth.'})


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        payload = {
            'grant_type': 'authorization_code',
            'code': code
        }

        response = requests.post(f'{AUTH_SERVICE}/token', json=payload)     # request access token

        if response.status_code == 200:
            token_data = response.json()
            store_token_data(token_data)                                    # store token data in session

            # retrieve spotify user id & store it in the session
            headers = get_sp_request_headers()
            response = requests.get(f'{SPOTIFY_SERVICE}/user', headers=headers)

            if response.status_code == 200:
                session['user_id'] = response.json().get('id')
                return redirect('/userhome')                                # after access token is received & stored, redirect to the userhome 
            else:
                return jsonify({'error': 'Failed to fetch user profile from Spotify service'})
        else:
            return jsonify({'error': 'Failed to obtain access token from authentication service'})
    else:
        return jsonify({'error': 'Authorization code not found.'})
    
    
@app.route('/userhome')
def userhome():
    try:
        headers = get_sp_request_headers()
        response = requests.get(f'{SPOTIFY_SERVICE}/user', headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            user_data = response.json()
            return render_template('user-home.html', title=f'{session['user_id'].upper()}  Home') # jsonify(user_data) # render_template('user-home.html', title=f'{session['user_id'].upper() Home}')
        else:
            return jsonify({'error': 'Failed to fetch user profile from Spotify service'}), response.status_code
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

#------------------- HELPER FUNCTIONS -------------------
def extract_track_info(track):
    """
    Extracts track information from spotify API track data
    """
    new_track = {}
    artist_names = [artist['name'] for artist in track['artists']]
    track_artists = ', '.join(artist_names)
    new_track['name'] = track['name']
    new_track['artist'] = track_artists
    new_track['duration_seconds'] = round(track['duration_ms'] / 1000.0)
    minute, second = divmod(new_track['duration_seconds'], 60)
    new_track['duration'] = '{:02}:{:02}'.format(minute, second)
    new_track['album_img'] = track['album']['images'][-2]['url']
    return new_track


def extract_artist_info(artist):
    """
    Extracts artist information from spotify API artist data
    """
    new_artist = {}
    new_artist['name'] = artist['name']
    new_artist['genres'] = artist['genres']
    new_artist['artist_id'] = artist['id']
    new_artist['image_url'] = artist['images'][0]['url']  # just grab first image
    new_artist['popularity'] = artist['popularity']
    return new_artist


def get_user_top(term, item_type):
    """
    Makes request to spotify service to retrieve top 10 tracks or artists for the spcified time frame (term).

    :param term: term length of the requested data, can be: short, medium, long
    :param item_type: type of data to get, can be: artists, tracks
    :return: array of dictionaries of the top items
    """
    headers = get_sp_request_headers()
    payload = {
        'term' : term,
        'type' : item_type
        }
    
    response = requests.get(f'{SPOTIFY_SERVICE}/user/top', headers=headers, params=payload)

    if item_type == 'tracks':
        top_items = [extract_track_info(track) for track in response.json()['items']]
    else:
        top_items = [extract_artist_info(track) for track in response.json()['items']]  # array of dictionaries

    return top_items


def get_top_genres(top_artists):
    """
    Determines user's top genres based on the genres of their top artists.

    :param top_artists: list of dictionaires containing user's top 10 artists
    :return: array of user's top 5 genres
    """
    genre_counts = Counter() # init counter

    # iterate over artists & update genre counts
    for artist in top_artists:
        genre_counts.update(artist['genres'])

    return [genre[0] for genre in genre_counts.most_common(5)]


def generate_wrap(term):
    """
    Generates a summary or 'wrap' of the user's top tracks, artists, and genres for the specified timeframe (term).

    :param term: term length of the requested data, can be: short, medium, long
    :return: dictionary containing the summary data
    """
    summary = {}            # the wrap
    summary['term'] = term.split('_')[0]
    summary['datetime'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    # user top tracks (top 10)
    top_tracks = get_user_top(term=term, item_type='tracks')
    summary['top_tracks'] = top_tracks

    # user top artists (top 10)
    top_artists = get_user_top(term=term, item_type='artists')
    summary['top_artists'] = top_artists

    # extract their top genres from top artist
    summary['top_genres'] = get_top_genres(top_artists)

    return summary


@app.route('/wrap', methods=['GET'])
def wrap():
    term = request.args.get('term') 
    summary = generate_wrap(f'{term}_term')
    MongoDBService(DATABASE).save_summary(session['user_id'], summary)  # save wrap to mongodb
    return render_template('user-home.html', title=f'{session['user_id'].upper()}  Home', summary=summary) 


@app.route('/wrap-home', methods=['GET'])
def wrap_home():
    return render_template('wrap-home.html')


@app.route('/my-wraps', methods=['GET', 'POST'])
def my_wraps():
    if request.method == 'POST':
        index = request.form['index']
        return jsonify(MongoDBService(DATABASE).get_summary_by_index(session['user_id'], int(index)))
    return jsonify(MongoDBService(DATABASE).get_summaries(session['user_id']))


@app.route('/my-wraps/delete', methods=['GET', 'POST'])
def delete_my_wraps():
    if request.method == 'POST':
        index = request.form['index']
        return jsonify(MongoDBService(DATABASE).delete_summary_by_index(session['user_id'], int(index)))
    return jsonify(MongoDBService(DATABASE).delete_all_summaries(session['user_id']))


@app.route('/my-wraps/<index>', methods=['GET'])
def get_my_wrap_by_index(index):
    return jsonify(MongoDBService(DATABASE).get_summary_by_index(session['user_id'], int(index)))

@app.route('/my-wraps/delete/<index>', methods=['GET'])
def delete_my_wrap_by_index(index):
    return jsonify(MongoDBService(DATABASE).delete_summary_by_index(session['user_id'], int(index)))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

dashboard.bind(app) # for monitoring dashboard

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)

