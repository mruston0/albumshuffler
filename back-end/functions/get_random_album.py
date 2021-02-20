import os
import json
import jwt
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
        claims = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        album = AlbumShufflerRepo(user_album_count_cache).get_random_album_spotify(claims['id'])

        return {
            "statusCode": 200,
            "body": json.dumps(album)
        }
    else:
        return {
            "statusCode": 401
        }