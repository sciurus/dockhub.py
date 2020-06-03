I wrote this because docker hub is stupid. Or at least seems that way.

Longer explanation:

Dockerhub limits the number of groups that can be seen in their web UI.
There is no way, for example, to see more than __n__ groups should you 
have that many (__n__ being a number around 110). For that reason,
any groups > 110 are completely unmanagable from the web UI.

This script is written for mozilla's use (specifically the
[mozilla-services](https://github.com/mozilla-services)) group. YMMV, but
it should be quite adaptable to anyone else's needs.
