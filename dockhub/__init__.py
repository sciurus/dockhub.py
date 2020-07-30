#!/usr/bin/env python3

from functools import wraps
import json
from os import getenv
import sys

import click
import requests


CONTENT_HEADER = {'Content-Type': 'application/json', 'charset': 'utf-8'}
DOCKERHUB_URL = 'https://hub.docker.com/v2'


def handle_http_errors(fun):
    """Wrap function with exception handling for common HTTP errors."""
    @wraps(fun)
    def _handle_http_errors(*args, **kwargs):
        try:
            return fun(*args, **kwargs)

        except requests.ConnectionError as exc:
            raise click.ClickException(f'Unable to connect to dockerhub: {exc}')
        except requests.HTTPError as exc:
            raise click.ClickException(f'HTTPError: {exc}')
        except requests.Timeout as exc:
            raise click.ClickException(f'Timeout: {exc}')
        except requests.TooManyRedirects as exc:
            raise click.ClickException(f'Too many redirects encountered: {exc}')

    return _handle_http_errors


def die(msg):
    """Print a message and exit with 1 status code."""
    click.echo(click.style(msg, fg="red"))
    sys.exit(1)


@handle_http_errors
def get_auth_token():
    docker_api_url = f'{DOCKERHUB_URL}/users/login/'
    username = getenv('DH_USERNAME', '').strip()
    if not username:
        die('For security, you must set your username as the variable DH_USERNAME in your ENV')

    password = getenv('DH_PASSWORD', '').strip()
    if not password:
        die('For security, you must set your password as the variable DH_PASSWORD in your ENV')

    auth = {"username": username, "password": password}
    auth_request = requests.post(docker_api_url, headers=CONTENT_HEADER, json=auth)
    if auth_request.status_code == 200:
        return auth_request.json()['token']
    else:
        die('Non-200 response received from DockerHub. Verify your credentials and try again')


@handle_http_errors
def get_group_id(auth_header, dh_group):
    # We need the group id to add the group to the repo later on
    docker_api_url = f'{DOCKERHUB_URL}/orgs/mozilla/groups/{dh_group}'
    group = requests.get(docker_api_url, headers=auth_header)
    if group.status_code == 200:
        return group.json()['id']
    else:
        die("Non-200 response form DockerHub. Verify your group name and try agin")


@handle_http_errors
def dump_group_info(auth_header, dh_group):
    group_url = f'{DOCKERHUB_URL}/orgs/mozilla/groups/{dh_group}'
    group_members_url = f'{group_url}/members'

    group = requests.get(group_url, headers=auth_header)
    if group.status_code == 200:
        print(f'group information for {dh_group}')
        print(json.dumps(group.json(), indent=2, sort_keys=True))
    else:
        die("Non-200 response form DockerHub. Verify your group name and try agin")

    members = requests.get(group_members_url, headers=auth_header)
    if group.status_code == 200:
        print(f'Membership information for {dh_group}')
        print(json.dumps(members.json(), indent=2, sort_keys=True))
    else:
        die("Non-200 response form DockerHub. Verify your group name and try agin")


@handle_http_errors
def add_user_to_group(auth_header, dh_user, dh_group, group_id):
    group_members_url = f'{DOCKERHUB_URL}/orgs/mozilla/groups/{dh_group}/members/'
    additional_headers = {**auth_header, **CONTENT_HEADER}
    add_user_json = {"member": dh_user}

    add_user = requests.post(group_members_url,
                             headers=additional_headers,
                             json=add_user_json)
    if add_user.status_code == 200:
        # Ensure the user has been added by pulling the list of members
        members = requests.get(group_members_url, headers=auth_header)
        if members.status_code == 200:
            # https://stackoverflow.com/questions/8653516/python-list-of-dictionaries-search
            if next((x for x in members.json() if x['username'] == f'{dh_user}'), None):
                print(f'Added {dh_user} to {dh_group}')
            else:
                die(f'Unknown error adding {dh_user} to {dh_group}')
        else:
            die(f'Could not verify {dh_user} has been added to {dh_group}. Caveat emptor!')
    else:
        die('Non-200 response from DockerHub. Review all the things and try again')


@handle_http_errors
def dump_user_info(auth_header, dh_user):
    user_url = f'{DOCKERHUB_URL}/users/{dh_user}'

    user = requests.get(user_url, headers=auth_header)
    if user.status_code == 200:
        print(f'User information for {dh_user}')
        print(json.dumps(user.json(), indent=2, sort_keys=True))
    else:
        die("Non-200 response form DockerHub. Verify the specified user name and try agin")


@handle_http_errors
def remove_user_from_group(auth_header, dh_user, dh_group):
    group_members_url = f'{DOCKERHUB_URL}/orgs/mozilla/groups/{dh_group}/members'
    user_group_members_url = f'{DOCKERHUB_URL}/orgs/mozilla/groups/{dh_group}/members/{dh_user}'
    additional_headers = {**auth_header, **CONTENT_HEADER}

    removed_user = requests.delete(user_group_members_url, headers=additional_headers)
    if removed_user.status_code == 204:
        members = requests.get(group_members_url, headers=auth_header)
        if members.status_code == 200:
            # https://stackoverflow.com/questions/8653516/python-list-of-dictionaries-search
            if next((x for x in members.json() if x['username'] == f'{dh_user}'), None):
                die(f'Unknown error removing {dh_user} from {dh_group}')
            else:
                print(f'Removed {dh_user} from {dh_group}')
        else:
            die(f'Could not verify {dh_user} has been removed from {dh_group}. Caveat emptor!')
    else:
        die("Non-200 response form DockerHub. I give up.")


@handle_http_errors
def add_group_to_repo(auth_header, dh_group, dh_repo, group_id):
    docker_api_url = f'{DOCKERHUB_URL}/repositories/mozilla/{dh_repo}/groups/'
    additional_headers = {**auth_header, **CONTENT_HEADER}
    add_group_json = {'group_id': group_id, 'permission': 'write'}

    add_group = requests.post(docker_api_url,
                              headers=additional_headers,
                              json=add_group_json)
    if add_group.status_code == 200:
        if add_group.json()[0]['group_id'] == group_id:
            print(f'Granted {dh_group} write access to {dh_repo}')
        else:
            die(f'Unknown error adding {dh_group} to {dh_repo}')
    else:
        die('Non-200 response from DockerHub. Review all the things and try again')


@handle_http_errors
def dump_repo_info(auth_header, dh_repo):
    # We're only gonna dump permissions and basic stats for the repo
    repo_url = f'{DOCKERHUB_URL}/repositories/mozilla/{dh_repo}'
    repo_permissions_url = f'{repo_url}/groups/'

    repo = requests.get(repo_url, headers=auth_header)
    repo_perms = requests.get(repo_permissions_url, headers=auth_header)
    if repo.status_code == 200 and repo_perms.status_code == 200:
        print(f'Repo information for {dh_repo}')
        r = {**repo.json(), **repo_perms.json()}
        print(json.dumps(r, indent=2, sort_keys=True))
    else:
        die("Non-200 response form DockerHub. Verify the specified repo name and try agin")


def remove_group_from_repo(auth_header, dh_group):
    pass


@click.command()
@click.option('-r', '--dh_repo', default=None, help='DockerHub repo you want to add the group to with r/w access', required=False)
@click.option('-g', '--dh_group', default=None, help='DockerHub group you want to add a user to', required=False)
@click.option('-u', '--dh_user', default=None, help='DockerHub user you want to add to the group (most likely, mzcs<something>)', required=False)
@click.option('-a', '--action', default="list", type=click.Choice(['list', 'add', 'remove']), help='What action to take: add, list (default), or remove', required=False)
@click.option('-f', '--force', "force", is_flag=True, help='Force the action of removing a group from a repo. Only group and repo can be set when using this option', required=False)
def main(dh_repo, dh_group, dh_user, action, force):
    """
    For this script to work properly, You'll need to export your DockerHub Username and
    password (DH_USERNAME/DH_PASSWORD) in your ENV.

    Be sure to have created both your group and your repo prior to running this script!

    Our SOP is to add users to groups, groups to repos. While you can add users directly
    to repos, that's not the way we do things, so it's not covered here.

    This is especially relevant to removals; We remove users from groups, not groups from
    repos.

    """
    token = get_auth_token()
    auth_header = {'Authorization': f'JWT {token}'}
    if action == "list":
        if dh_group is not None:
            dump_group_info(auth_header, dh_group)
        if dh_user is not None:
            dump_user_info(auth_header, dh_user)
        if dh_repo is not None:
            dump_repo_info(auth_header, dh_repo)

    elif action == "add" or action == "remove":
        group_id = get_group_id(auth_header, dh_group)
        if action == "add":
            add_user_to_group(auth_header, dh_user, dh_group, group_id)
            if dh_repo is not None:
                add_group_to_repo(auth_header, dh_group, dh_repo, group_id)
        else:
            if action == "remove":
                remove_user_from_group(auth_header, dh_user, dh_group)
                if dh_user is None and dh_repo is not None and force is not None:
                    remove_group_from_repo(dh_repo, dh_group)


if __name__ == "__main__":
    main()
