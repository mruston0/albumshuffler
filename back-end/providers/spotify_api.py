import requests
import os

SPOTIFY_APP_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_APP_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']

DEFAULT_REDIRECT_URI = "http://lvh.me:3000/spotifyauth"

class SpotifyApi:

    def get_access_tokens(self, code, redirect_uri=DEFAULT_REDIRECT_URI):
        url = 'https://accounts.spotify.com/api/token'
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": SPOTIFY_APP_ID,
            "client_secret": SPOTIFY_APP_SECRET
        }
        resp = requests.post(
            url=url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        return resp.json()

    def get_access_token_from_refresh_token(self, refresh_token):
        url = 'https://accounts.spotify.com/api/token'
        resp = requests.post(
            url=url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": SPOTIFY_APP_ID,
                "client_secret": SPOTIFY_APP_SECRET
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        return resp.json()

    def get_user_profile(self, access_token):
        url = 'https://api.spotify.com/v1/me'
        resp = requests.get(
            url=url,
            headers={'Authorization': f'Bearer {access_token}'})
        return resp.json()


    def get_albums(self, access_token):
        return self._get_albums(access_token)

    def _get_albums(self, access_token, url=None):
        if not url:
            url = 'https://api.spotify.com/v1/me/albums'
        response = requests.get(
            url=url, 
            headers={'Authorization': f'Bearer {access_token}'})
        response_json = response.json()
        albums = []
        for item in response_json['items']:
            albums.append(item['album'])
        if response_json.get('next'):
            albums.extend(self._get_albums(access_token, url=response_json['next']))
        return albums



    