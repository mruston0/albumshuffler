import os
import json
import boto3
import jwt
from os import access
from providers.spotify_api import SpotifyApi
from repositories.album_shuffler_repo import AlbumShufflerRepo
from queues.album_import_queue import AlbumImportQueue
import constants

jwt_secret = os.environ['JWT_SECRET']

def handler(event, context):
    
    print(event)
    code = event.get('queryStringParameters', {}).get('code')
    host = event['headers']['host']
    redirect_uri = f"https://{host}/spotifyauth"
    if not code:
        raise Exception(f"Code not found in query string for event {event}")

    spotify_api = SpotifyApi()
    tokens = spotify_api.get_access_tokens(code, redirect_uri)
    if 'error' in tokens:
        return {
            "statusCode": 400,
            "body": f"Spotify auth error: {tokens['error']} - {tokens['error_description']}"
    }
    
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
    
    jwt_token = jwt.encode(
      {
        'id': user_profile["id"], 
        'service':constants.SERVICE_DEEZER
      },
      jwt_secret, 
      algorithm='HS256'
    )

    response = {
        "statusCode": 302,
        "headers": {
            "Location": f"http://lvh.me:3000/spotify.html?token={jwt_token}"        # replace this when I have production URLs configured.
        }
    }

    return response