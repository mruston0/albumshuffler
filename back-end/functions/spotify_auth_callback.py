import json
import boto3
from os import access
from providers.spotify_api import SpotifyApi
from repositories.album_shuffler_repo import AlbumShufflerRepo
from queues.album_import_queue import AlbumImportQueue
import constants

def handler(event, context):
    
    code = event.get('queryStringParameters', {}).get('code')
    host = event['Headers']['orign']
    redirect_uri = f"{host}/spotifyauth"
    if not code:
        raise Exception(f"Code not found in query string for event {event}")

    spotify_api = SpotifyApi()
    tokens = spotify_api.get_access_tokens(code, redirect_uri)
    user_profile = spotify_api.get_user_profile(access_token=tokens['access_token'])
    # Check if user exists, create new user if not exists
    spotify_user = AlbumShufflerRepo().get_spotify_user(user_profile['id'])
    if not spotify_user:
        user_payload = {
            'id' : user_profile['id'],
            'display_name': user_profile['display_name'],
            'image': user_profile.get('images')[0].get('url'),     # This might have bugs
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'access_token_expiry': tokens['expires_in']
        }
        AlbumShufflerRepo.create_spotify_user(user_payload)

    AlbumImportQueue().add(user_profile['id'], service=constants.SERVICE_SPOTIFY)
    
    # Mint a JWT for the user and return that to the client.

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response