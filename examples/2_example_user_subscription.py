from typegenie import authenticator, Deployment

# Assuming that the deployment with id `my-new-deployment` exists.
deployment_id = 'my-new-deployment'

# Authentication
DEPLOYMENT_ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXBsb3ltZW50X2lkIjoibXktbmV3LWRlcGxveW1lbnQiLCJhY2NvdW50X2lkIjoiS1VORE9TRSIsImV4cCI6MTYyMDIyNDgwMiwic2VxX251bSI6MSwiaWF0IjoxNjIwMjIxMjAyfQ.09uD4GnJW0RmkPMiDH-65xVYV2Bf7rFy4o3qC5uZyII'

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

# USER SUBSCRIPTION MANAGEMENT

# List user
users = deployment.users()
print('List Users:', users)

user_id = 'my-new-user'
for idx in range(len(users)):
    user = users[idx]
    if user.id == user_id:
        # (Unsafe) Deletion method 2
        user = users.pop(idx)
        del user
        break


# Create a new user
user = deployment.users(user_id=user_id, create=True, metadata={})
print('Created User:', user)

# Delete a user
to_delete_user = deployment.users(user_id='to-be-user', metadata={}, create=True)
print('List Users (Before Deletion):', deployment.users())
del to_delete_user
print('List Users (After Deletion):', deployment.users())

# Get existing user
existing_user = deployment.users(user_id=user_id)
print('Existing User:', existing_user)

# Update metadata of existing user
existing_user.update(metadata={'Test': False, 'trial': 'yes'})
print('Updated User:', existing_user)

# Get access token
print('Get User Access Token:', deployment.get_user_access_token(user_id=user_id))

