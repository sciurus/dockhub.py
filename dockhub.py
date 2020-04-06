#!/usr/bin/env python3
import requests
import click
from os import getenv
from sys import exit


def die(msg=None, exception=None):
    if msg is not None:
        print(f'{msg}')
    if exception is not None:
        print(f'{exception}')
    exit(1)


def get_auth_token():
    docker_api_url = f'{dockerhub_url}/users/login/'
    username = getenv('DH_USERNAME')
    if username is not None:
        password = getenv('DH_PASSWORD')
        if password is not None:
            auth = {"username": username, "password": password}
            try:
                auth_request = requests.post(docker_api_url, headers=content_header, json=auth)
                if auth_request.status_code == 200:
                    return auth_request.json()['token']
                else:
                    die('Non-200 response received from DockerHub. Verify your credentials and try again')
            except requests.ConnectionError as e:
                die('Unable to connect to dockerhub:', e)
            except requests.HTTPError as e:
                die('HTTPError:', e)
            except requests.Timeout as e:
                die('Timeout error:', e)
            except requests.TooManyRedirects as e:
                die('Too many redirects encountered:', e)
        else:
            die('For security, you must set your password as the variable DH_PASSWORD in your ENV')
    else:
        die('For security, you must set your username as the variable DH_USERNAME in your ENV')


def get_team(auth_header, dh_team):
    docker_api_url = f'{dockerhub_url}/orgs/mozilla/groups/{dh_team}'
    try:
        team = requests.post(docker_api_url, headers=auth_header)
        if team.status_code == 200:
            return team.json()['id']
        else:
            die("Non-200 response form DockerHub. Verify your team name and try agin")
    except requests.ConnectionError as e:
        die('Unable to connect to dockerhub:', e)
    except requests.HTTPError as e:
        die('HTTPError:', e)
    except requests.Timeout as e:
        die('Timeout error:', e)
    except requests.TooManyRedirects as e:
        die('Too many redirects encountered:', e)


def add_user_to_team(auth_header, dh_user, dh_team, group_id):
    docker_api_url = f'{dockerhub_url}/orgs/mozilla/groups/{dh_team}/members/'
    add_user_headers = {**auth_header, **content_header}
    add_user_json = {"member": dh_user}
    try:
        add_user = requests.post(docker_api_url,
                                 headers=add_user_headers,
                                 json=add_user_json)
        if add_user.status_code == 200:
            if add_user.json()[0]['username'] == dh_user:
                print(f'Added {dh_user} to {dh_team}')
            else:
                die(f'Unknown error adding {dh_user} to {dh_team}')
        else:
            die('Non-200 response from DockerHub. Review all the things and try again')
    except requests.ConnectionError as e:
        die('Unable to connect to dockerhub:', e)
    except requests.HTTPError as e:
        die('HTTPError:', e)
    except requests.Timeout as e:
        die('Timeout error:', e)
    except requests.TooManyRedirects as e:
        die('Too many redirects encountered:', e)


def add_team_to_repo(auth_header, dh_team, dh_repo, group_id):
    docker_api_url = f'{dockerhub_url}/repositories/mozilla/{dh_repo}/groups/'
    add_team_headers = {**auth_header, **content_header}
    add_team_json = {'group_id': group_id, 'permission': 'write'}
    try:
        add_team = requests.post(docker_api_url,
                                 headers=add_team_headers,
                                 json=add_team_json)
        if add_team.status_code == 200:
            if add_team.json()[0]['group_id'] == group_id:
                print(f'Granted {dh_team} write access to {dh_repo}')
            else:
                die(f'Unknown error adding {dh_team} to {dh_repo}')
        else:
            die('Non-200 response from DockerHub. Review all the things and try again')
    except requests.ConnectionError as e:
        die('Unable to connect to dockerhub:', e)
    except requests.HTTPError as e:
        die('HTTPError:', e)
    except requests.Timeout as e:
        die('Timeout error:', e)
    except requests.TooManyRedirects as e:
        die('Too many redirects encountered:', e)


@click.command()
@click.option('-r', '--dh_repo', default=None, help='DockerHub repo you want to add the team to with r/w access', required=True)
@click.option('-t', '--dh_team', default=None, help='DockerHub team you want to add a user to', required=True)
@click.option('-u', '--dh_user', default=None, help='DockerHub user you want to add to the team (most likely, mzcs<something>)', required=True)
def main(dh_repo, dh_team, dh_user):
    """
    For this script to work properly, You'll need to export your DockerHub Username and
    password (DH_USERNAME/DH_PASSWORD) in your ENV.

    Be sure to have created both your Team and your repo prior to running this script!
    """
    token = get_auth_token()
    auth_header = {'Authorization': f'JWT {token}'}
    group_id = get_team(auth_header, dh_team)
    add_user_to_team(auth_header, dh_user, dh_team, group_id)


if __name__ == "__main__":
    dockerhub_url = 'https://hub.docker.com/v2'
    content_header = {'Content-Type': 'application/json'}
    main()
