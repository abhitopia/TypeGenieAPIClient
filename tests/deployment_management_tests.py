from typegenie import authenticator, Deployment
import os

ACCOUNT_USERNAME = os.getenv('username')
ACCOUNT_PASSWORD = os.getenv('password')

authenticator.authenticate_account(username=ACCOUNT_USERNAME, password=ACCOUNT_PASSWORD)

# Enabling sandbox environment. Ignore this!
# authenticator.enable_sandbox()

'''Deployment management tests'''
def test_list_deployments():
    deployments = Deployment.list()
    print('List Deployments:', deployments)
    return deployments

def test_deployment_safe_delete(deployments, deployment_id):
    for idx in range(len(deployments)):
        deployment = deployments[idx]
        if deployment.id == deployment_id:
            # Delete existing client from the account. Note: Deletes it on the backend also.
            # (Safe) Deletion method 1
            deployment.delete()
            del deployment
            break

def test_deployment_unsafe_delete(deployments, deployment_id):
    for idx in range(len(deployments)):
        deployment = deployments[idx]
        if deployment.id == deployment_id:
            deployment = deployments.pop(idx)
            del deployment
            break

def test_create_deployment(deployment_id, metadata={'test': True}):
    new_deployment = Deployment.create(deployment_id=deployment_id, metadata=metadata)
    print('New Deployment:', new_deployment)
    return new_deployment

def test_create_and_delete_repository(deployment_id='to-be-deleted'):
    to_delete_deployment = Deployment.create(deployment_id=deployment_id, metadata={})
    print('List Deployments (Before Deletion):', Deployment.list())
    del to_delete_deployment
    print('List Deployments (After Deletion):', Deployment.list())

deployment_id = 'my-new-deployment'

def test_get_existing_repository(deployment_id):
    existing_deployment = Deployment.get(deployment_id=deployment_id)
    print('Existing Deployment:', existing_deployment)
    return existing_deployment

def test_update_deployment(deployment, metadata = {'Test': False, 'trial': 'yes'}):
    # Update metadata of existing deployment
    deployment.update(metadata=metadata)
    print('Updated Deployment:', deployment)

def test_deployment_token_fetch(deployment_id):
    # Get access token for a particular deployment
    token_dict = Deployment.get_access_token(deployment_id=deployment_id)
    print('Deployment Access Token:', token_dict)
    return token_dict



if __name__=='__main__':
    test_list_deployments()
    new_deployment = test_create_deployment('test-deployment')
    test_update_deployment(new_deployment)
    test_get_existing_repository(new_deployment.id)
    test_deployment_token_fetch(new_deployment.id)
    deployments = test_list_deployments()
    test_deployment_safe_delete(deployments, new_deployment.id)
    test_create_and_delete_repository()
    test_list_deployments()
