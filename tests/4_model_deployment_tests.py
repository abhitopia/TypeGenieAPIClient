from testconfig import authenticated_deployment, dataset_id, user_id, deployment_id, dialogues, clean_test_environment


def test_model_config_fetch(authenticated_deployment):
    assert (isinstance(authenticated_deployment.configs, list) and len(authenticated_deployment.configs) > 0)


def test_model_deployment(authenticated_deployment):
    configs = authenticated_deployment.configs
    # create dataset and upload dialogues
    # authenticated_deployment.deploy(config=configs[3], datasets=)
    assert True


def test_model_undeployment(authenticated_deployment):
    # deploy model
    # authenticated_deployment.undeploy()
    assert True

