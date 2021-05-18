from typegenie import authenticator, Deployment, Dialogue, Event, EventType, Author
from datetime import datetime

# Assuming that the deployment with id `my-new-deployment` exists.
deployment_id = 'my-new-deployment'

# Authentication
DEPLOYMENT_ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXBsb3ltZW50X2lkIjoibXktbmV3LWRlcGxveW1lbnQiLCJhY2NvdW50X2lkIjoiS1VORE9TRSIsImV4cCI6MTYxNjcxMTI2Miwic2VxX251bSI6MSwiaWF0IjoxNjE2NzA3NjYyfQ.pyZabJxQu4FIsisSlmfCRfMoQrJICx3ilQBcQQsnmhc'

ACCOUNT_USERNAME = None
ACCOUNT_PASSWORD = None

# Enabling sandbox environment. Ignore this!
authenticator.enable_sandbox()

if DEPLOYMENT_ACCESS_TOKEN is not None:
    authenticator.authenticate_deployment(token=DEPLOYMENT_ACCESS_TOKEN)
elif ACCOUNT_USERNAME is not None and ACCOUNT_PASSWORD is not None:
    authenticator.authenticate_account(username=ACCOUNT_USERNAME, password=ACCOUNT_PASSWORD)
    # Then you can fallback to higher level API automatically by running following command
    authenticator.enable_auto_fallback()
else:
    raise RuntimeError('You must either have a deployment access token or account credentials')

# Furthermore, since the access token expires automatically after a while, you can enable token auto renew using
authenticator.enable_auto_renew()

# Assuming that the deployment with id `my-new-deployment` exists.
deployment = Deployment.get(deployment_id=deployment_id)
print('Deployment:', deployment)

# Model training and undeployment
available_configs = deployment.configs
print('Available Configs:', available_configs)


model_config = available_configs[0]
# Assumes `my-new-dataset` dataset exists
dataset = deployment.datasets(dataset_id='my-new-dataset')
datasets = [deployment.datasets(dataset_id='my-new-dataset')]

print('Deployment History(Before deployment):', deployment.history())
deployment.deploy(config=model_config, datasets=datasets)
print('Deployment History(After deployment):', deployment.history())

# Undeploy
deployment.undeploy()
print('Deployment History(After un-deployment):', deployment.history())

# Deploy again
deployment.deploy(config=model_config, datasets=datasets)
