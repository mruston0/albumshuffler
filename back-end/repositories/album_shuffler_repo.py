import json
import os
import boto3
import datetime
import random
import logging
import constants

_logger = logging.getLogger(__name__)

from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ.get('ALBUM_SHUFFLER_TABLE', 'dev-AlbumShufflerTable')
SPOTIFY_ALBUM_LIMIT = 3000

class AlbumShufflerRepo:

    def __init__(self, user_album_count_cache=None):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(TABLE_NAME)
        self.user_album_count_cache = user_album_count_cache if user_album_count_cache else {}
    
    def get_spotify_user(self, id):
        return self._get_user(id, 'SPOTIFY')

    def get_deezer_user(self, id):
        return self._get_user(id, 'DEEZER')
    
    def _get_user(self, id, service):
        item = self.table.get_item(Key={'id': id, 'sortKey': f'USER#{service}'})
        return item.get('Item')

    def create_spotify_user(self, payload):
        self.table.put_item(
            Item={
                'id': payload["id"],
                'sortKey': 'USER#SPOTIFY',
                'name': payload['display_name'],
                'image': payload['image'],
                'access_token': payload['access_token'],
                'refresh_token': payload['refresh_token'],
                'access_token_expiry': payload['access_token_expiry']
            }
        )


    def get_album_spotify(self, user_id, album_id):
        item = self.table.get_item(Key={'id': user_id, 'sortKey': f'ALBUM#{constants.SERVICE_SPOTIFY}#{album_id}'})
        return item.get('Item')

    def get_album_ids_spotify(self, user_id):
        
        query_args = {
            'ProjectionExpression':'album_id',
            'KeyConditionExpression':
                Key('id').eq(str(user_id)) & Key('sortKey').begins_with(f'ALBUM#{constants.SERVICE_SPOTIFY}'),
            'Limit':100
        }
        
        response = self.table.query(**query_args)

        items = response['Items']

        while 'LastEvaluatedKey' in response:
            query_args['ExclusiveStartKey'] = response.get('LastEvaluatedKey')
            response = self.table.query(**query_args)
            items.extend(response['Items'])
        
        return items

    def get_user_album_count_spotify(self, user_id):
        item = self.table.get_item(Key={'id': user_id, 'sortKey': f'ALBUMCOUNT#{constants.SERVICE_SPOTIFY}'})
        return item.get('Item')

    def get_random_album_spotify(self, user_id):
        count = self.user_album_count_cache.get('user_id', self.get_user_album_count_spotify(user_id)['count'])
        self.user_album_count_cache['user_id'] = count
        album_choice = random.randrange(0, count)
        album = self.get_album_spotify(user_id, album_choice)
        return album

    def save_albums_spotify(self, user_id, albums):
        self.table.put_item(
            Item={
                'id': user_id,
                'sortKey': 'ALBUMIMPORTPROCESS#SPOTIFY',
                'status': 'RUNNING',
                'started': datetime.datetime.utcnow().isoformat()
            }
        )

        import_status = None

        try:
            # Deleting the existing albums
            album_count = self.get_user_album_count_spotify(user_id)['count'] + 1
            with self.table.batch_writer() as batch:
                for i in range(1, int(album_count)):
                    batch.delete_item(
                        Key={
                            'id': str(user_id),
                            'sortKey': f'ALBUM#{constants.SERVICE_SPOTIFY}#{i}'
                        })
        
            # Add in the new albums
            count = 1
            with self.table.batch_writer() as batch:
                for a in albums:
                    print(f"User {user_id} saving album {a['name']}")
                    batch.put_item(
                        Item={
                            'id': user_id,
                            'sortKey': f'ALBUM#{constants.SERVICE_SPOTIFY}#{count}',
                            'album_id': str(a['id']),
                            'title': a['name'],
                            'cover_small': a['images'][2]['url'],
                            'cover_medium': a['images'][1]['url'],
                            'cover_big': a['images'][0]['url'],
                            # Big assumption here that we want the first artist.... we can fix this another time.
                            'artist': {
                                'id': str(a['artists'][0]['id']),
                                'name': a['artists'][0]['name']
                            }
                        }
                    )
                    count = count+1
                    if count >= SPOTIFY_ALBUM_LIMIT:
                        break
            
            self.table.put_item(
            Item={
                'id': user_id,
                'sortKey': 'ALBUMCOUNT#SPOTIFY',
                'count': count,
                'updated': datetime.datetime.utcnow().isoformat()
            })

            import_status = 'COMPLETED'
        except Exception as exc:
            import_status = 'FAILED'
            _logger.exception(msg="Error importing Spotify albums for user", exc_info=exc, extra={'user_id': user_id})
        
        self.table.put_item(
            Item={
                'id': user_id,
                'sortKey': 'ALBUMIMPORTPROCESS#SPOTIFY',
                'status': import_status,
                'completed': datetime.datetime.utcnow().isoformat()
            }
        )
        