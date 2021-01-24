import json

def handler(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    # parse the JWT, get the user_id and then pull a album....

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response