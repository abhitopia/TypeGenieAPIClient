from typegenie import authenticator, Deployment, Dialogue, Event, EventType, Author
from testconfig import authenticated_deployment, dataset_id, user_id, deployment_id, dialogues


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

