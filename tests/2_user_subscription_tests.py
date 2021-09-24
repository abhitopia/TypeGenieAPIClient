from typegenie import authenticator
from requests import HTTPError
import json
import os
from testconfig import authenticated_deployment, clean_test_environment, user_id, authenticator, deployment_id


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
