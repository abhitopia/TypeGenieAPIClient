from requests import HTTPError, Response
import os
from typegenie import authenticator, Deployment
import json
import pytest
from testconfig import deployment, clean_test_environment, deployment_id, metadata


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
