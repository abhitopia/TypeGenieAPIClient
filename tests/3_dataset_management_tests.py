from testconfig import authenticated_deployment, dataset_id, clean_test_environment, dialogues, user_id
from requests import HTTPError, Response
import json

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