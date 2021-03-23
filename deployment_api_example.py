from typegenie import authenticator, Deployment

# Assuming that the deployment with id `my-new-deployment` exists.
deployment_id = 'my-new-deployment'

# Authentication
DEPLOYMENT_ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXBsb3ltZW50X2lkIjoibXktbmV3LWRlcGxveW1lbnQiLCJhY2NvdW50X2lkIjoiS1VORE9TRSIsImV4cCI6MTYxNjUyNDQyOSwic2VxX251bSI6MSwiaWF0IjoxNjE2NTIwODI5fQ.ytTqArLJ8PrM3RM_3g_OTv8wWcBl_NoLmxU-sSmdq3Q'
ACCOUNT_USERNAME = None
ACCOUNT_PASSWORD = None

if DEPLOYMENT_ACCESS_TOKEN is not None:
    authenticator.authenticate_deployment(deployment_id=deployment_id, token=DEPLOYMENT_ACCESS_TOKEN)
elif ACCOUNT_USERNAME is not None and ACCOUNT_PASSWORD is not None:
    authenticator.authenticate_account(username=ACCOUNT_USERNAME, password=ACCOUNT_PASSWORD)
    # Then you can fallback to higher level API automatically by running following command
    authenticator.enable_auto_fallback()
else:
    raise RuntimeError('You must either have a client access token or account credentials')

# Furthermore, since the access token expires automatically after a while, you can enable token auto renew using
authenticator.enable_auto_renew()


# Assuming that the deployment with id `my-new-deployment` exists.
deployment = Deployment.get(deployment_id=deployment_id)
print('Deployment:', deployment)

# List datasets
datasets = deployment.datasets()
print('List Datasets:', datasets)

