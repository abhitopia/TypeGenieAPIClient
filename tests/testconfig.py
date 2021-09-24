import os
import pytest
from typegenie import authenticator, Deployment, Event, EventType, Author, Dialogue
from datetime import datetime

ACCOUNT_USERNAME = os.getenv('username')
ACCOUNT_PASSWORD = os.getenv('password')
authenticator.authenticate_account(username=ACCOUNT_USERNAME, password=ACCOUNT_PASSWORD)
deployment_id = 'test-deployment'
metadata = {'test': True}
user_id = 'test_user'
dataset_id = 'dataset-id'

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


dialogues = [my_dialogue_1, my_dialogue_2]


@pytest.fixture
def deployment():
    yield Deployment.create(deployment_id=deployment_id, metadata=metadata)


@pytest.fixture(autouse=True)
def clean_test_environment():
    deployments = Deployment.list()
    if len(deployments) > 0:
        for idx in range(len(deployments)):
            deployment = deployments[idx]
            deployment.delete()
            del deployment
            break

@pytest.fixture
def authenticated_deployment():
    deployment = Deployment.create(deployment_id, {})
    deployment_access_token = Deployment.get_access_token(deployment_id=deployment_id)
    authenticator.authenticate_deployment(token=deployment_access_token["token"])
    yield deployment


