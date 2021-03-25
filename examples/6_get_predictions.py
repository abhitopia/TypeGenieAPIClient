from typegenie import authenticator, User


# Authentication
USER_ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoibXktbmV3LXVzZXIiLCJkZXBsb3ltZW50X2lkIjoibXktbmV3LWRlcGxveW1lbnQiLCJhY2NvdW50X2lkIjoiS1VORE9TRSIsInNlcV9udW0iOjEsImV4cCI6MTYxNjcwOTYxOCwiaWF0IjoxNjE2NzA2MDE4fQ.J0vcawZBJVxcO28_ouxTwIOUSABgTbkPo5d3WSUa-xk'

DEPLOYMENT_ACCESS_TOKEN = None
ACCOUNT_USERNAME = None
ACCOUNT_PASSWORD = None

if USER_ACCESS_TOKEN is not None:
    authenticator.authenticate_user(token=USER_ACCESS_TOKEN)
if DEPLOYMENT_ACCESS_TOKEN is not None:
    authenticator.authenticate_deployment(token=DEPLOYMENT_ACCESS_TOKEN)
    # Then you can fallback to higher level API automatically by running following command
    authenticator.enable_auto_fallback()
elif ACCOUNT_USERNAME is not None and ACCOUNT_PASSWORD is not None:
    authenticator.authenticate_account(username=ACCOUNT_USERNAME, password=ACCOUNT_PASSWORD)
    # Then you can fallback to higher level API automatically by running following command
    authenticator.enable_auto_fallback()
else:
    raise RuntimeError('You must either have a user/deployment access token or account credentials')

# Furthermore, since the access token expires automatically after a while, you can enable token auto renew using
authenticator.enable_auto_renew()


# Assuming that the user with id `my-new-user` exists.
user_id = 'my-new-user'
deployment_id = 'my-new-deployment'

user = User.get(user_id=user_id, deployment_id=deployment_id)
print(user)