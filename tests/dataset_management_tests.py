from deployment_management_tests import test_create_deployment, test_deployment_safe_delete, \
    test_deployment_token_fetch, test_list_deployments
from user_subscription_tests import test_authenticate_deployment


def test_list_datasets(deployment):
    # List datasets
    datasets = deployment.datasets()
    print('List Datasets:', datasets)
    return datasets


def test_delete_dataset(datasets, dataset_id):
    for idx in range(len(datasets)):
        dataset = datasets[idx]
        if dataset.id == dataset_id:
            dataset.delete()
            del dataset
            break


def test_create_dataset(deployment, dataset_id):
    # Create a dataset
    dataset = deployment.datasets(dataset_id=dataset_id, create=True, metadata={})
    print('Created Dataset:', dataset)
    return dataset


def test_update_dataset(dataset, metadata={'Test': True, 'trial': 'yes', 'Others': 'stuff'}):
    dataset.update(metadata=metadata)
    print('Updated Dataset:', dataset)


def test_get_specific_dataset(deployment, dataset_id):
    dataset = deployment.datasets(dataset_id=dataset_id)
    return dataset


if __name__ == "__main__":
    try:
        # Create and authenticate deployment
        deployment = test_create_deployment('test-deployment')
        token = test_deployment_token_fetch(deployment.id)
        test_authenticate_deployment(token["token"])
        # List, create, update and delete dataset
        test_list_datasets(deployment)
        dataset = test_create_dataset(deployment, 'test-dataset')
        test_update_dataset(dataset)
        test_get_specific_dataset(deployment, dataset.id)
        datasets = test_list_datasets(deployment)
        test_delete_dataset(datasets, dataset_id=dataset.id)
        # Delete deployment
        deployments = test_list_deployments()
        test_deployment_safe_delete(deployments, deployment.id)
        test_list_deployments()

    except Exception:
        deployments = test_list_deployments()
        test_deployment_safe_delete(deployments, 'test-deployment')