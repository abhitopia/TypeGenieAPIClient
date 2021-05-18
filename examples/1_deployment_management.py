from typegenie import authenticator, Deployment
from examples.creds import USERNAME, PASSWORD


ACCOUNT_USERNAME = USERNAME
ACCOUNT_PASSWORD = PASSWORD

# Enabling sandbox environment. Ignore this!
authenticator.enable_sandbox()


# Authenticate with account credentials
authenticator.authenticate_account(username=ACCOUNT_USERNAME, password=ACCOUNT_PASSWORD)

# List existing deployments
deployments = Deployment.list()
print('List Deployments:', deployments)

deployment_id = 'my-new-deployment'
for idx in range(len(deployments)):
    deployment = deployments[idx]
    if deployment.id == deployment_id:
        # Delete existing client from the account. Note: Deletes it on the backend also.

        # (Safe) Deletion method 1
        deployment.delete()
        del deployment

        # (Unsafe) Deletion method 2
        deployment = deployments.pop(idx)
        del deployment
        # Notice that for `del deployment` to work (without needing `deployment.delete()`, all reference of
        # `deployment` must be removed. That is why we do `deployment.pop(idx)` to remove it's reference from the
        # list `deployments`. When in doubt, use `deployment.delete()` before calling `del deployment`
        break

# Create a new deployment
new_deployment = Deployment.create(deployment_id=deployment_id, metadata={'test': True})
print('New Deployment:', new_deployment)

# Delete a deployment
to_delete_deployment = Deployment.create(deployment_id='to-be-deleted', metadata={})
print('List Deployments (Before Deletion):', Deployment.list())
del to_delete_deployment
print('List Deployments (After Deletion):', Deployment.list())

# Get existing deployment
existing_deployment = Deployment.get(deployment_id=deployment_id)
print('Existing Deployment:', existing_deployment)

# Update metadata of existing deployment
existing_deployment.update(metadata={'Test': False, 'trial': 'yes'})
print('Updated Deployment:', existing_deployment)

# Get access token for a particular deployment
token_dict = Deployment.get_access_token(deployment_id=deployment_id)
print('Deployment Access Token:', token_dict)
