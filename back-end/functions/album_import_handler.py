import json
import sentry
import logging
from queues.album_import_queue import AlbumImportQueue

_logger = logging.getLogger(__name__)

def handler(event, context):
    _logger.info(event)
    for r in event.get('Records', []):
        try:
            payload = json.loads(r['body'])
            if 'id' not in payload and 'service' not in payload:
                raise Exception(f"Invalid SQS payload received {payload}")
            AlbumImportQueue().process(payload['id'], payload['service'])
        except Exception as exc:
            _logger.exception(exc)


    
