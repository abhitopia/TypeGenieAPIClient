from typegenie import authenticator, Deployment, Dialogue, Event, EventType, Author

from deployment_management_tests import test_create_deployment, test_deployment_safe_delete, \
    test_deployment_token_fetch, test_list_deployments
from user_subscription_tests import test_authenticate_deployment, test_create_user, test_delete_user, test_user_token_fetch
from dataset_management_tests import test_create_dataset
from upload_dialogues_tests import test_upload_to_dataset
from datetime import datetime


events = [Event(author_id='lost-soul-visitor',
                value='What is love?',
                event=EventType.MESSAGE,
                timestamp=datetime.utcnow(),
                author=Author.USER),
          Event(author_id='my-new-user',  # Note this is an agent already added as user to deployment
                value="Oh baby, don't hurt me",
                event=EventType.MESSAGE,
                timestamp=datetime.utcnow(),  # This should be time at which the event happened
                author=Author.AGENT)
          ]





def test_complete_model_deployment(deployment):
    # Create dataset
    dataset = test_create_dataset(deployment, 'test-dataset')
    test_upload_to_dataset(dataset)
    # Deploy model
    available_configs = deployment.configs
    print(available_configs)
    config = available_configs[3]
    deployment.deploy(config=config, datasets=[dataset])



def test_full_cycle(deployment):
    test_complete_model_deployment(deployment)
    user = test_create_user(deployment, 'test-user')
    user_token = test_user_token_fetch(deployment, user.id)
    authenticator.authenticate_user(token=user_token["token"])
    print("User authenticated!")
    session_id = user.create_session()
    print("Session {} successfully created!".format(session_id))


if __name__ == "__main__":
    try:
        # Create and authenticate deployment
        deployment = test_create_deployment('test-deployment')
        token = test_deployment_token_fetch(deployment.id)
        test_authenticate_deployment(token["token"])
        test_full_cycle(deployment)
        print("Sleep for 30...")
        #Undeploy model
        deployment.undeploy()
        #Delete deployment
        deployments = test_list_deployments()
        test_deployment_safe_delete(deployments, deployment.id)
        test_list_deployments()

    except Exception as e:
        print("Error: {}".format(e))
        print("Will delete deployment!")
        deployments = test_list_deployments()
        test_deployment_safe_delete(deployments, 'test-deployment')
        print("Done")

