import json
from pathlib import Path
import random

import requests
from .lib import Deployment, Dialogue, authenticator
from .autocomplete import AutoComplete
import click
from box import Box


@click.command()
@click.option('-u', '--username', type=str, required=False, help="Account Username", default=None)
@click.option('-p', '--password', type=str, required=False, help="Account Password", default=None)
@click.option('-dpi', '--deployment_id', type=str, required=True, help="Deployment ID")
@click.option('-t', '--token', type=str, required=False, help="Deployment access token.")
@click.option('-dsi', '--dataset_id', type=str, required=True, help="DatasetID to be used for testing.")
@click.option('-ui', '--user-id', type=str, required=True, help="User ID within the Deployment")
@click.option('--sandbox', is_flag=True, default=False, help="By default, production environment is used. Set this "
                                                                "flag to use sandbox environment")
@click.option('--cache-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True), default='/tmp',
              help="Path where dataset is downloaded")
@click.option('-n', '--num-dialogues', default=500, type=int, help="Number of dialogues to load")
@click.option('--interactive', is_flag=True, default=False, help="Set to continue interaction")
@click.option('--unprompted', is_flag=True, default=False, help="Show completions even when unprompted")
@click.option('--multiline', is_flag=True, default=False, help="Set to allow multiline completions")
@click.option('--no-context', is_flag=True, default=False, help="Disabled passing any context")
def main(**params):
    """Simulate TypeGenie on your command line!

    KeyBindings:

    - Arrow <Up> or <DOWN> to select a completion

    - <TAB> to accept the selected completion

    - <SHIFT+TAB> to only accept the first word of the selected completion

    - <CTL+C> to start a new dialogue

    - <CTL+C> in succession to exit
    """
    params = Box(params)

    if params.sandbox:
        authenticator.enable_sandbox()

    if params.token is None:
        assert_str = "Either specify deployment `token` or account `username` and `password`"
        assert all(p is not None for p in [params.username, params.password]), assert_str
        authenticator.authenticate_account(username=params.username, password=params.password)
    else:
        authenticator.authenticate_deployment(token=params.token)

    authenticator.enable_auto_fallback()
    authenticator.enable_auto_renew()
    deployment = Deployment.get(deployment_id=params.deployment_id)
    print(f'Loaded Deployment: {deployment}')

    available_datasets = deployment.datasets()
    available_users = deployment.users()
    assert any(
        d.id == params.dataset_id for d in available_datasets), f"{params.dataset_id} not found in the deployment!"
    assert any(
        u.id == params.user_id for u in available_users), f"{params.user_id} not found in the deployment!"
    dataset = [d for d in available_datasets if d.id == params.dataset_id][0]
    user = [u for u in available_users if u.id == params.user_id][0]

    print(f'Downloading {dataset.num_dialogues} to {params.cache_dir}...')

    download_dir = Path(params.cache_dir) / dataset.id

    download_dir.mkdir(exist_ok=True, parents=True)
    download_links = dataset.get_download_links()

    dialogues = []
    for link in sorted(download_links, key=lambda x: x['url']):
        file_name = link['url'].split('?')[0].split('/')[-1]
        output_file = download_dir / file_name
        if not output_file.exists():
            data = requests.get(link['url']).json()
            json.dump(data, output_file.open('w'), indent=4)
        else:
            data = json.load(output_file.open('r'))

        for d in data:
            if random.random() < 0.05 and len(dialogues) < params.num_dialogues:
                dialogues.append(Dialogue.from_dict(d))
        else:
            if len(dialogues) >= params.num_dialogues:
                break

    autocomplete = AutoComplete(user=user,
                                dialogue_dataset=dialogues,
                                unprompted=params.unprompted,
                                multiline=params.multiline,
                                no_context=params.no_context,
                                interactive=params.interactive)

    autocomplete.interact()


if __name__ == '__main__':
    main()
