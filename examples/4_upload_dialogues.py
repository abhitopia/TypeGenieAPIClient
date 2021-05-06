from typegenie import authenticator, Deployment, Dialogue, Event, EventType, Author
from datetime import datetime

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

# Dialogue upload

# Create Dialogue

my_dialogue_1 = Dialogue(dialogue_id='my-dialogue-1', metadata={'title': "What is love?"})

my_dialogue_1.events.append(Event(author_id='lost-soul-visitor',
                                  value='What is love?',
                                  event=EventType.MESSAGE,
                                  timestamp=datetime.utcnow(),
                                  author=Author.USER))
my_dialogue_1.events.append(Event(author_id='my-new-user',  # Note this is an agent already added as user to deployment
                                  value="Oh baby, don't hurt me",
                                  event=EventType.MESSAGE,
                                  timestamp=datetime.utcnow(),  # This should be time at which the event happened
                                  author=Author.AGENT))
my_dialogue_1.events.append(Event(author_id='lost-soul-visitor',
                                  value="Don't hurt me, no more",
                                  event=EventType.MESSAGE,
                                  timestamp=datetime.utcnow(),
                                  author=Author.AGENT))

my_dialogue_2 = Dialogue(dialogue_id='my-dialogue-2', metadata={'Artist': "Ping Floyd"})

my_dialogue_2.events.append(Event(author_id='system',
                                  value='Jam session begins:',
                                  event=EventType.CONTEXTUAL,
                                  timestamp=datetime.utcnow(),
                                  author=Author.SYSTEM))
my_dialogue_2.events.append(Event(author_id='pink-floyd-fan',
                                  value='Where were you when I was burned and broken? And where were you when I was '
                                        'hurt and I was helpless?',
                                  event=EventType.MESSAGE,
                                  timestamp=datetime.utcnow(),
                                  author=Author.USER))
my_dialogue_2.events.append(Event(author_id='my-new-user',  # Note this is an agent already added as user to deployment
                                  value="While the days slipped by from my window watching, I was staring straight "
                                        "into the shining sun. 'Cause the things you say and the things you do "
                                        "surround me",
                                  event=EventType.MESSAGE,
                                  timestamp=datetime.utcnow(),
                                  author=Author.AGENT))
my_dialogue_2.events.append(Event(author_id='pink-floyd-fan',
                                  value="Dying to believe in what you heard",
                                  event=EventType.MESSAGE,
                                  timestamp=datetime.utcnow(),
                                  author=Author.AGENT))


# Get existing dataset
dataset_id = 'my-new-dataset'  # Assumes that this already exists
existing_dataset = deployment.datasets(dataset_id=dataset_id)
print('Existing Dataset:', existing_dataset)

# upload dialogues
existing_dataset.upload(dialogues=[my_dialogue_1, my_dialogue_2]*100000)


# download
download_links = existing_dataset.get_download_links()
print(download_links)
doSomething = 1
