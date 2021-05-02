import os
import json
import jwt
import datetime

import sentry

import constants
from repositories.album_shuffler_repo import AlbumShufflerRepo
from queues.album_import_queue import AlbumImportQueue

jwt_secret = os.environ['JWT_SECRET']
PREFIX = 'Bearer'

DELAY=300

def handler(event, context):
    print(event)
    auth_header = event.get('headers', {}).get('authorization')
    if auth_header:
        bearer, _, token = auth_header.partition(' ')
        if bearer != PREFIX:
            raise ValueError('Invalid token')
        claims = jwt.decode(token, jwt_secret, algorithms=['HS256'])

        album_count_obj = AlbumShufflerRepo().get_user_album_count_spotify(claims['id'])
        last_updated = album_count_obj.get('updated', datetime.datetime.min)

        updating = False

        # Only refresh once per day
        if last_updated.date() < datetime.datetime.utcnow().date():
            # Delay refresh for 5 minutes. We don't want to be deleting and refreshing the user's
            # albums while they are actively using the shuffler
            print(f"Refreshing albums in {DELAY}s for User {claims['id']}. Last Updated {last_updated}.")
            AlbumImportQueue().add(claims['id'], service=constants.SERVICE_SPOTIFY, delay=DELAY)
            updating = True     

        return {
            "statusCode": 200,
            "body": json.dumps({
                "updating": updating
            })
        }
    else:
        return {
            "statusCode": 401
        }