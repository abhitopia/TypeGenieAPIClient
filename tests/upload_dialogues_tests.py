from typegenie import authenticator, Deployment, Dialogue, Event, EventType, Author

from deployment_management_tests import test_create_deployment, test_deployment_safe_delete, \
    test_deployment_token_fetch, test_list_deployments
from user_subscription_tests import test_authenticate_deployment
from dataset_management_tests import test_create_dataset
from datetime import datetime


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


def test_upload_to_dataset(dataset, dialogues=[my_dialogue_1, my_dialogue_2] * 100):
    dataset.upload(dialogues)

def test_get_download_link(dataset):
    download_links = dataset.get_download_links()
    print(download_links)


if __name__ == "__main__":
    try:
        # Create and authenticate deployment
        deployment = test_create_deployment('test-deployment')
        token = test_deployment_token_fetch(deployment.id)
        test_authenticate_deployment(token["token"])
        # Create dataset
        dataset = test_create_dataset(deployment, 'test-dataset')
        test_upload_to_dataset(dataset)
        test_get_download_link(dataset)
        #Delete deployment
        deployments = test_list_deployments()
        test_deployment_safe_delete(deployments, deployment.id)
        test_list_deployments()
    except Exception:
        deployments = test_list_deployments()
        test_deployment_safe_delete(deployments, 'test-deployment')