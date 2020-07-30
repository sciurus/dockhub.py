# Dockhub.py

I wrote this because docker hub is stupid. Or at least seems that way.

Longer explanation:

Dockerhub limits the number of groups that can be seen in their web UI.
There is no way, for example, to see more than __n__ groups should you 
have that many (__n__ being a number around 110). For that reason,
any groups > 110 are completely unmanagable from the web UI.

This script is written for mozilla's use (specifically the
[mozilla-services](https://github.com/mozilla-services)) group. YMMV, but
it should be quite adaptable to anyone else's needs.

## Installation: 

  1. Create virtualenv (or whatever you prefer for I-downloaded-it-from-the-internet code)
  1. Activate your venv
  1. cd \<checkout dir\>
  1. run `pip install .`

## Usage:

1. Export your dockerhub username/password as the ENV vars DH_USERNAME and DH_PASSWORD. The script will not run without this.

1. Sample uses:

   `$ dockhub --action add --dh_user <dockerhub username> --dh_repo <dockerhub repo name> --dh_group <dockerhub group>`

   Add \<dockerhub username\> to the \<dockerhub group\> and then grant that group r+w permissions to \<dockerhub repo name\>

   `$dockhub --action list --dh_repo <repo name>`

   Display group membership and permissions for \<repo name\>

   `$dockhub --action add --dh_user <user name> --dh_group <group name>`

   Add \<user name\> to \<group name\>

   Finally, you can also remove users from groups

   `$ dockhub --action remove --dh_user <user name> --dh_group \<group name\>`

   Removes \<user name\> from \<group name\>

## For development:

1. Install dev requirements:

   `$ pip install -r requirements-dev.txt`

1. Run tests:

   `$ pytest`
