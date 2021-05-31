import os
import json
import jwt
import sentry
from repositories.album_shuffler_repo import AlbumShufflerRepo

jwt_secret = os.environ['JWT_SECRET']
PREFIX = 'Bearer'

user_album_count_cache = {}

def handler(event, context):
    print(event)
    auth_header = event.get('headers', {}).get('authorization')
    if auth_header:
        bearer, _, token = auth_header.partition(' ')
        if bearer != PREFIX:
            raise ValueError('Invalid token')
        if not token:
            return status_401()
        claims = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        sentry.set_user(claims['id'])
        album = AlbumShufflerRepo(user_album_count_cache).get_random_album_spotify(claims['id'])

        return {
            "statusCode": 200,
            "body": json.dumps(album)
        }
    else:
        return status_401()

def status_401():
    return { "statusCode": 401 }