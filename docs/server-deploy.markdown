<!-- encoding: utf-8 -->
<!-- Created on Jan 15, 2015, by fuzhou.chen@ruuxee.com -->

#Deploy RuuXee server environment.

This document describes how to deploy ruuxee server environment on a
Linux (for production) or Mac (for development).

## General

Ruuxee project is deployed in a "clean" environment, based on Python
virtualenv tool. We do it to make sure it comes with fixed dependency
list.

Surely developers can choose not to use virtualenv but just directly use
ruuxee module under src/server. However, this is NOT RECOMMENDED in
production environment.

## Deploy debug environment

###A quick start for developers

We use a Bash script, ruuxee-deploy.sh, to deploy Ruuxee's virtualenv
environment. You can find it under scripts/ folder. A simple command
line looks like below (assume you work in Debian/Ubuntu Linux box):

    sudo apt-get install python-dev
    sudo mkdir /home/www/ruuxee.com
    cd $HOME/ruuxee-website
    bash scripts/ruuxee-server-deploy.sh /home/www/ruuxee.com
    cd /home/www/ruuxee.com
    bash ./bin/activate

The commands above will help you deploy an isolated environment under
/home/www/ruuxee.com folder, with necessary Python dependencies and
ruuxee packages installed.

After that, you can start a mock server (no database, no cache, with
fake dataset pre-created) by command below:

    python bin/mockserver.py

Now a server is started in http://localhost:5000 and ready to accept
commands, for example:

    curl --request GET http://localhost:5000/person/fuzhou.chen

Please note that this is a fake server, which does not support
authentication, so it always authenticate current user as
bourne.zhu.

###More details on deployment
A full command line of ruuxee-deploy.sh looks like below:

    ruuxee-server-deploy.sh <env_root_folder> [pip_dependency_list_file]

Please note that the second parameter is optional. If nothing is
specified, it will use default one, scripts/ruuxee-server-env-deps.txt.

In most environment, developers can choose to use default dependency
list. The second parameter is useful only when developers want to test
a new environment with updated dependency list.


##Deploy Production enviornment

TBD
