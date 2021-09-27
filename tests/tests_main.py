from requests import HTTPError, Response
import os
from typegenie import authenticator, Deployment
import json
import pytest
from testconfig import deployment, clean_test_environment, deployment_id, metadata, user_id, dialogues, dataset_id, authenticated_deployment


"""Deployment management tests"""


def test_list_deployment():
    deployments = Deployment.list()
    assert (isinstance(deployments, list))


def test_deployment_safe_delete(deployment):
    deployments = Deployment.list()
    for idx in range(len(deployments)):
        deployment = deployments[idx]
        if deployment.id == deployment_id:
            # Delete existing client from the account. Note: Deletes it on the backend also.
            # (Safe) Deletion method 1
            deployment.delete()
            del deployment
            break
    assert (len(Deployment.list()) == 0)


def test_create_deployment(deployment):
    assert (len(Deployment.list()) == 1)


def test_exception_on_repeated_deployment(deployment):
    try:
        Deployment.create(deployment_id=deployment_id, metadata=metadata)
    except HTTPError as e:
        assert (e.response.status_code == 400 and json.loads(e.response.content.decode("utf-8"))[
            "error"] == "Deployment with id={} already exists. Deployment id should be unique.".format(deployment_id))


def test_update_deployment(deployment):
    # Update metadata of existing deployment
    deployment.update(metadata={'Test': False, 'trial': 'yes'})
    updated_deployment = Deployment.get(deployment_id)
    assert (updated_deployment.to_dict()["metadata"] == {'Test': False, 'trial': 'yes'})


def test_get_existing_repository(deployment):
    existing_deployment = Deployment.get(deployment_id=deployment_id)
    assert (existing_deployment.to_dict()["id"] == deployment_id)


def test_deployment_token_fetch(deployment):
    # Get access token for a particular deployment
    token_dict = Deployment.get_access_token(deployment_id=deployment_id)
    assert (isinstance(token_dict["token"], str))


"""User subscription tests"""

def test_list_users(authenticated_deployment):
    users = authenticated_deployment.users()
    assert (isinstance(users, list))


def test_create_user(authenticated_deployment):
    authenticated_deployment.users(user_id=user_id, create=True, metadata={})
    users = authenticated_deployment.users()
    assert (len(users) == 1 and users[0].id == user_id)


def test_exception_on_repeated_user(authenticated_deployment):
    try:
        authenticated_deployment.users(user_id=user_id, create=True, metadata={})
        authenticated_deployment.users(user_id=user_id, create=True, metadata={})
    except HTTPError as e:
        assert (e.response.status_code == 400 and json.loads(e.response.content.decode("utf-8"))[
            "error"] == "User with id={} already exists.".format(user_id))


def test_delete_user(authenticated_deployment):
    authenticated_deployment.users(user_id=user_id, create=True, metadata={})
    users = authenticated_deployment.users()
    for idx in range(len(users)):
        user = users[idx]
        if user.id == user_id:
            user.delete()
            del user
            break
    users_after_delete = authenticated_deployment.users()
    assert (len(users_after_delete) == 0)


def test_update_user(authenticated_deployment):
    # Get existing user
    authenticated_deployment.users(user_id=user_id, create=True, metadata={})
    existing_user = authenticated_deployment.users(user_id=user_id)
    # Update metadata of existing user
    existing_user.update(metadata={'Test': False, 'trial': 'yes'})
    updated_user = authenticated_deployment.users(user_id=user_id)
    assert (updated_user.to_dict()["metadata"] == {'Test': False, 'trial': 'yes'})


def test_user_token_fetch(authenticated_deployment):
    authenticated_deployment.users(user_id=user_id, create=True, metadata={})
    user_token = authenticated_deployment.get_user_access_token(user_id=user_id)
    assert ("token" in user_token and isinstance(user_token["token"], str))


def test_create_user_session(authenticated_deployment):
    user = authenticated_deployment.users(user_id=user_id, create=True, metadata={})
    user_token = authenticated_deployment.get_user_access_token(user_id=user_id)
    authenticator.authenticate_user(token=user_token["token"])
    session_id = user.create_session()
    assert (isinstance(session_id, str) and session_id is not None)


def test_exception_on_non_authenticated_user_session_request(authenticated_deployment):
    try:
        user = authenticated_deployment.users(user_id=user_id, create=True, metadata={})
        user.create_session()
    except HTTPError as e:
        assert (e.response.status_code == 403)

"""Dataset management tests"""

def test_list_datasets(authenticated_deployment):
    datasets = authenticated_deployment.datasets()
    assert (isinstance(datasets, list))


def test_delete_dataset(authenticated_deployment):
    authenticated_deployment.datasets(dataset_id=dataset_id, create=True, metadata={})
    datasets = authenticated_deployment.datasets()
    for idx in range(len(datasets)):
        dataset = datasets[idx]
        if dataset.id == dataset_id:
            dataset.delete()
            del dataset
            break
    updated_datasets = authenticated_deployment.datasets()
    assert (len(updated_datasets) == 0)


def test_create_dataset(authenticated_deployment):
    # Create a dataset
    authenticated_deployment.datasets(dataset_id=dataset_id, create=True, metadata={})
    assert (len(authenticated_deployment.datasets()) == 1)


def test_update_dataset(authenticated_deployment):
    dataset = authenticated_deployment.datasets(dataset_id=dataset_id, create=True, metadata={})
    dataset.update(metadata={'Test': True, 'trial': 'yes', 'Others': 'stuff'})
    dataset = authenticated_deployment.datasets(dataset_id=dataset_id)
    assert (dataset.to_dict()["metadata"] == {'Test': True, 'trial': 'yes', 'Others': 'stuff'})



def test_upload_to_dataset(authenticated_deployment):
    dataset = authenticated_deployment.datasets(dataset_id=dataset_id, create=True, metadata={})
    dataset.upload(dialogues * 50)
    updated_dataset = authenticated_deployment.datasets(dataset_id=dataset_id)
    assert(updated_dataset.to_dict()["num_dialogues"] == 100)


def test_get_download_link(authenticated_deployment):
    dataset = authenticated_deployment.datasets(dataset_id=dataset_id, create=True, metadata={})
    dataset.upload(dialogues * 10)
    download_links = dataset.get_download_links()
    assert(isinstance(download_links, list) and "url" in download_links[0] and isinstance(download_links[0]["url"], str))


def test_exception_on_dataset_exceeded_size(authenticated_deployment):
    try:
        dataset = authenticated_deployment.datasets(dataset_id=dataset_id, create=True, metadata={})
        dataset.upload(dialogues * 30000)
    except HTTPError as e:
        assert (e.response.status_code == 400 and json.loads(e.response.content.decode("utf-8"))[
            "error"] == "Num of dialogues uploaded should not be more than 50000.".format(user_id))


"""Model deployment tests"""

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
