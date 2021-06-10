import time
from datetime import datetime, timezone
from typing import List
from json import JSONDecodeError

from threading import Thread

import requests
from requests.auth import HTTPBasicAuth

BASE_URL = 'https://api.typegenie.net/api/v1'
SANDBOX_URL = 'https://staging-api.typegenie.net/api/v1'


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class AutoRenewThread(Thread):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self._running = False

    def run(self):
        while self._running:
            result = self.api.renew_token(inplace=True)
            expires_at = datetime.strptime(result['expires_at'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            seconds_till_expiry = (expires_at - datetime.utcnow().replace(tzinfo=timezone.utc)).seconds
            renew_after = max(0, seconds_till_expiry - 100)
            time.sleep(renew_after)

    def start(self):
        if not self._running:
            self._running = True
            super().start()

    def stop(self):
        self._running = False


class API:
    COMMON_PREFIX = ''

    def __init__(self, sandbox=False):
        self._session = requests.Session()
        self._session.headers.update({
            'Content-type': 'application/json',
            'Accept': 'application/json'
        })
        self._sandbox = sandbox

    def _get_url(self, end_point):
        if self._sandbox:
            return f'{SANDBOX_URL}{self.COMMON_PREFIX}{end_point}'
        else:
            return f'{BASE_URL}{self.COMMON_PREFIX}{end_point}'

    def _request(self, func, url, **kwargs):
        try:
            resp = func(url, **kwargs)
            resp.raise_for_status()
            r = resp.json()
            return r['result']
        except requests.exceptions.HTTPError as err:
            try:
                r = resp.json()
                err.args = list(err.args) + [f'Reason: {r["error"]}']
                raise err
            except JSONDecodeError:
                raise err

    def _get(self, endpoint):
        url = self._get_url(endpoint)
        return self._request(self._session.get, url=url)

    def _delete(self, endpoint):
        url = self._get_url(endpoint)
        return self._request(self._session.delete, url=url)

    def _post(self, endpoint, json):
        url = self._get_url(endpoint)
        return self._request(self._session.post, url=url, json=json)

    def _put(self, endpoint, json):
        url = self._get_url(endpoint)
        return self._request(self._session.put, url=url, json=json)


class AccountAPI(API):
    COMMON_PREFIX = '/account'
    DEPLOYMENT_SUFFIX = '/deployment'

    def __init__(self, username, password, sandbox=False):
        super().__init__(sandbox=sandbox)
        self._session.auth = HTTPBasicAuth(username=username, password=password)

    def list_deployments(self):
        return self._get(self.DEPLOYMENT_SUFFIX)

    def create_deployment(self, deployment_id, metadata={}):
        assert isinstance(deployment_id, str)
        payload = {'id': deployment_id, 'metadata': metadata}
        return self._post(self.DEPLOYMENT_SUFFIX, json=payload)

    def update_deployement(self, deployment_id, metadata):
        assert isinstance(deployment_id, str)
        payload = {'metadata': metadata}
        return self._put(f'{self.DEPLOYMENT_SUFFIX}/{deployment_id}', json=payload)

    def delete_deployment(self, deployment_id):
        assert isinstance(deployment_id, str)
        return self._delete(f'{self.DEPLOYMENT_SUFFIX}/{deployment_id}')

    def get_deployment(self, deployment_id):
        assert isinstance(deployment_id, str)
        return self._get(f'{self.DEPLOYMENT_SUFFIX}/{deployment_id}')

    def get_deployment_access_token(self, deployment_id):
        assert isinstance(deployment_id, str)
        return self._get(f'{self.DEPLOYMENT_SUFFIX}/{deployment_id}/token')


class DeploymentAPI(API):
    COMMON_PREFIX = '/deployment'
    USER_SUFFIX = '/user'
    MODEL_SUFFIX = '/model'
    DATASET_SUFFIX = '/dataset'

    def __init__(self, token, sandbox=False):
        super().__init__(sandbox=sandbox)
        self._session.auth = BearerAuth(token=token)
        self._auto_renew = AutoRenewThread(api=self)

    def enable_auto_renew(self):
        self._auto_renew.start()

    def disable_auto_renew(self):
        self._auto_renew.stop()

    def info(self):
        return self._get('')

    def renew_token(self, inplace=False):
        result = self._get('/renew')
        if inplace:
            self._session.auth = BearerAuth(token=result['token'])
        return result

    # Dataset Endpoints
    def create_dataset(self, dataset_id, metadata={}):
        assert isinstance(dataset_id, str)
        payload = {'id': dataset_id, 'metadata': metadata}
        return self._post(self.DATASET_SUFFIX, json=payload)

    def list_datasets(self):
        return self._get(self.DATASET_SUFFIX)

    def get_dataset(self, dataset_id):
        assert isinstance(dataset_id, str)
        return self._get(f'{self.DATASET_SUFFIX}/{dataset_id}')

    def download_dataset(self, dataset_id):
        assert isinstance(dataset_id, str)
        return self._get(f'{self.DATASET_SUFFIX}/{dataset_id}/download')

    def update_dataset(self, dataset_id, metadata):
        assert isinstance(dataset_id, str)
        payload = {'metadata': metadata}
        return self._put(f'{self.DATASET_SUFFIX}/{dataset_id}', json=payload)

    def delete_dataset(self, dataset_id):
        assert isinstance(dataset_id, str)
        return self._delete(f'{self.DATASET_SUFFIX}/{dataset_id}')

    def upload_dialogues(self, dataset_id, dialogues):
        assert isinstance(dataset_id, str)
        payload = {'dialogues': dialogues}
        return self._post(f'{self.DATASET_SUFFIX}/{dataset_id}', json=payload)

    # Model Endpoints
    def list_model_configs(self):
        return self._get(f'{self.MODEL_SUFFIX}/configs')

    def deploy_model(self, dataset_ids: list, model_config_id):
        payload = {'dataset_ids': dataset_ids, 'configuration_id': model_config_id}
        return self._post(self.MODEL_SUFFIX, json=payload)

    def get_deployment_history(self):
        return self._get(self.MODEL_SUFFIX)

    def undeploy_model(self):
        return self._delete(self.MODEL_SUFFIX)

    # Agent Endpoints
    def add_user(self, user_id, metadata={}):
        assert isinstance(user_id, str)
        payload = {'id': user_id, 'metadata': metadata}
        return self._post(self.USER_SUFFIX, json=payload)

    def list_users(self):
        return self._get(f'{self.USER_SUFFIX}')

    def get_user(self, user_id):
        assert isinstance(user_id, str)
        return self._get(f'{self.USER_SUFFIX}/{user_id}')

    def update_user(self, user_id, metadata):
        assert isinstance(user_id, str)
        payload = {'metadata': metadata}
        return self._put(f'{self.USER_SUFFIX}/{user_id}', json=payload)

    def delete_user(self, user_id):
        assert isinstance(user_id, str)
        return self._delete(f'{self.USER_SUFFIX}/{user_id}')

    def get_user_access_token(self, user_id):
        assert isinstance(user_id, str)
        return self._get(f'{self.USER_SUFFIX}/{user_id}/token')


class UserAPI(API):
    COMMON_PREFIX = '/user'
    SESSION_SUFFIX = '/session'

    def __init__(self, token, sandbox=False):
        super().__init__(sandbox=sandbox)
        self._session.auth = BearerAuth(token=token)
        self._auto_renew = AutoRenewThread(api=self)

    def enable_auto_renew(self):
        self._auto_renew.start()

    def disable_auto_renew(self):
        self._auto_renew.stop()

    def info(self):
        return self._get('')

    def renew_token(self, inplace=False):
        result = self._get('/renew')
        if inplace:
            self._session.auth = BearerAuth(token=result['token'])
        return result

    def create_session(self):
        return self._post(self.SESSION_SUFFIX, json={})

    def get_completions(self, session_id, events: List[dict], query: str):
        assert isinstance(session_id, str)
        payload = {'query': query, 'events': events}
        return self._post(f'{self.SESSION_SUFFIX}/{session_id}/completions', json=payload)
