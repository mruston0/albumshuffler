import os
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

sentry_sdk.init(
    dsn="https://ccf14ba5afbf48b08d5a2b0c03e08fde@o603606.ingest.sentry.io/5744550",
    environment=os.environ.get('STAGE'),
    integrations=[AwsLambdaIntegration()],
    traces_sample_rate=1.0  
)

def set_user(user):
    sentry_sdk.set_user(user) if user else None