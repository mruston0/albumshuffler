import os
import json
import boto3
import constants
from repositories.album_shuffler_repo import AlbumShufflerRepo
from providers.spotify_api import SpotifyApi

ALBUM_IMPORT_QUEUE = os.environ.get('ALBUM_IMPORT_QUEUE')

class AlbumImportQueue:

    def add(self, user_id, service, delay=None):
        sqs = boto3.resource('sqs')
        queue = sqs.get_queue_by_name(QueueName=ALBUM_IMPORT_QUEUE)
        payload = {
            'id': user_id,
            'service': service
        }

        delay = delay if delay else 0

        queue.send_message(
            MessageBody=json.dumps(payload),
            DelaySeconds=delay
        )
    
    def process(self, user_id, service):
        if service == constants.SERVICE_SPOTIFY:
            return self._process_spotify(user_id)
        if service == constants.SERVICE_DEEZER:
            return self._process_deezer(user_id)
        raise Exception("Invalid service")
    
    def _process_spotify(self, user_id):
        repo = AlbumShufflerRepo()
        user = repo.get_spotify_user(user_id)
        # This could be optimized. We could check if our access_token is still good....
        # Also if another import is already running we shouldn't import again? (Do we really care?)
        spotify_api = SpotifyApi()
        tokens = spotify_api.get_access_token_from_refresh_token(user['refresh_token'])
        if 'error' in tokens:
            raise Exception(f"Error getting Spotify access token:  {tokens['error']} - {tokens['error_description']}")
        albums = spotify_api.get_albums(access_token=tokens['access_token'])
        repo.save_albums_spotify(user_id, albums)

    def _process_deezer(self, user_id):
        pass
