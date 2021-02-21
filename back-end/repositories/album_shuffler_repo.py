import json
import os
import boto3
import datetime
import random
import constants

TABLE_NAME = os.environ.get('ALBUM_SHUFFLER_TABLE', 'dev-AlbumShufflerTable')

class AlbumShufflerRepo:

    def __init__(self, user_album_count_cache=None):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(TABLE_NAME)
        self.user_album_count_cache = user_album_count_cache if user_album_count_cache else {}
    
    def get_spotify_user(self, id):
        return self.__get_user(id, 'SPOTIFY')

    def get_deezer_user(self, id):
        return self.__get_user(id, 'DEEZER')
    
    def __get_user(self, id, service):
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

    def create_deezer_user(self, payload):
        # TODO for Deezer support eventually
        pass

    def get_album_spotify(self, user_id, album_id):
        item = self.table.get_item(Key={'id': user_id, 'sortKey': f'ALBUM#{constants.SERVICE_SPOTIFY}#{album_id}'})
        return item.get('Item')

    def get_user_album_count_spotify(self, user_id):
        item = self.table.get_item(Key={'id': user_id, 'sortKey': f'ALBUMCOUNT#{constants.SERVICE_SPOTIFY}'})
        return item.get('Item')['count']

    def get_random_album_spotify(self, user_id):
        count = self.user_album_count_cache.get('user_id', self.get_user_album_count_spotify(user_id))
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

        count = 1
        with self.table.batch_writer() as batch:
            for a in albums:
                print(f"Saving album {a['name']}")
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
        
        self.table.put_item(
            Item={
                'id': user_id,
                'sortKey': 'ALBUMIMPORTPROCESS#SPOTIFY',
                'status': 'COMPLETED',
                'started': datetime.datetime.utcnow().isoformat()
            }
        )
        
        self.table.put_item(
            Item={
                'id': user_id,
                'sortKey': 'ALBUMCOUNT#SPOTIFY',
                'count': count,
            }
        )
    
    def save_albums_deezer(self, user_id):
        pass
        