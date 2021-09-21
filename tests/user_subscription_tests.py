from typegenie import authenticator, Deployment
from deployment_management_tests import test_create_deployment, test_deployment_safe_delete, test_deployment_token_fetch, test_list_deployments
import os

ACCOUNT_USERNAME = os.getenv('username')
ACCOUNT_PASSWORD = os.getenv('password')

authenticator.authenticate_account(username=ACCOUNT_USERNAME, password=ACCOUNT_PASSWORD)



# Assuming that the deployment with id `my-new-deployment` exists.
deployment_id = 'my-new-deployment'

# Authentication
# DEPLOYMENT_ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXBsb3ltZW50X2lkIjoibXktbmV3LWRlcGxveW1lbnQiLCJhY2NvdW50X2lkIjoiS1VORE9TRSIsImV4cCI6MTYyMDIyNDgwMiwic2VxX251bSI6MSwiaWF0IjoxNjIwMjIxMjAyfQ.09uD4GnJW0RmkPMiDH-65xVYV2Bf7rFy4o3qC5uZyII'



# Enabling sandbox environment. Ignore this!
# authenticator.enable_sandbox()
def test_authenticate_deployment(deployment_access_token):
    if deployment_access_token is not None:
        authenticator.authenticate_deployment(token=deployment_access_token)
    elif ACCOUNT_USERNAME is not None and ACCOUNT_PASSWORD is not None:
        authenticator.authenticate_account(username=ACCOUNT_USERNAME, password=ACCOUNT_PASSWORD)
        # Then you can fallback to higher level API automatically by running following command
        authenticator.enable_auto_fallback()
    else:
        raise RuntimeError('You must either have a deployment access token or account credentials')

    # Furthermore, since the access token expires automatically after a while, you can enable token auto renew using
    authenticator.enable_auto_renew()

def test_list_users(deployment_id):
    deployment = Deployment.get(deployment_id=deployment_id)
    users = deployment.users()
    print('List Users:', users)
    return users

def test_delete_user(users, user_id):
    for idx in range(len(users)):
        user = users[idx]
        if user.id == user_id:
            user.delete()
            del user
            break

def test_create_user(deployment, user_id):
    user = deployment.users(user_id=user_id, create=True, metadata={})
    print('Created User:', user)
    return user

def get_create_and_delete_user(deployment):
    # Create a new user


    # Delete a user
    to_delete_user = deployment.users(user_id='to-be-user', metadata={}, create=True)
    print('List Users (Before Deletion):', deployment.users())
    del to_delete_user
    print('List Users (After Deletion):', deployment.users())


def test_update_user(user_id):
    # Get existing user
    existing_user = deployment.users(user_id=user_id)
    print('Existing User:', existing_user)

    # Update metadata of existing user
    existing_user.update(metadata={'Test': False, 'trial': 'yes'})
    print('Updated User:', existing_user)


def test_user_token_fetch(deployment, user_id):
    user_token = deployment.get_user_access_token(user_id=user_id)
    print(user_token)
    return user_token

if __name__ == '__main__':
    deployment = test_create_deployment('test-deployment')
    token = test_deployment_token_fetch(deployment.id)
    test_authenticate_deployment(token["token"])
    user = test_create_user(deployment, 'test_user')
    test_list_users(deployment.id)
    test_update_user(user.id)
    users = test_list_users(deployment.id)
    test_delete_user(users, user.id)
    print("user deleted...")
    test_list_users(deployment.id)
    deployments = test_list_deployments()
    test_deployment_safe_delete(deployments, deployment.id)
    test_list_deployments()