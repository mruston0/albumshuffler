import json
from queues.album_import_queue import AlbumImportQueue

def handler(event, context):
    print(event)
    for r in event.get('Records', []):
        payload = json.loads(r['body'])
        if 'id' not in payload and 'service' not in payload:
            raise Exception(f"Invalid SQS payload received {payload}")
        AlbumImportQueue().process(payload['id'], payload['service'])

    
