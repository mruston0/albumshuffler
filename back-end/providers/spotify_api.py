import requests
import os

SPOTIFY_APP_ID = os.environ['SPOTIFY_APP_ID']
SPOTIFY_APP_SECRET = os.environ['SPOTIFY_APP_SECRET']

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
        """ {
                "display_name": "Matthew Ruston",
                "external_urls": {
                    "spotify": "https://open.spotify.com/user/12158538819"
                },
                "followers": {
                    "href": null,
                    "total": 4
                },
                "href": "https://api.spotify.com/v1/users/12158538819",
                "id": "12158538819",
                "images": [
                    {
                    "height": null,
                    "url": "https://scontent-ort2-2.xx.fbcdn.net/v/t1.0-1/p320x320/45493672_10101153213459008_4371065436356214784_n.jpg?_nc_cat=105&ccb=2&_nc_sid=0c64ff&_nc_ohc=DjkjjvD_htIAX8iQr5L&_nc_oc=AQmiwn8Cj_Dip_UrPsD69gzh0PVFCP0ouNth3VjuZGzYbBjpm15KIY8QTGT5utR5-qM&_nc_ht=scontent-ort2-2.xx&tp=6&oh=bee04974f182c813fbd9eb019fb9ea28&oe=60333112",
                    "width": null
                    }
                ],
                "type": "user",
                "uri": "spotify:user:12158538819"
            }
        """
        url = 'https://api.spotify.com/v1/me'
        resp = requests.get(
            url=url,
            headers={'Authorization': f'Bearer {access_token}'})
        return resp.json()


    def get_albums(self, access_token):
        return self.__get_albums(access_token)

    def __get_albums(self, access_token, url=None):
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
            print(f"Paging with {response_json.get('next')}")
            albums.extend(self.__get_albums(access_token, url=response_json['next']))
        return albums



    