<!-- encoding: utf-8 -->
<!-- Created on Jan 15, 2015, by fuzhou.chen@ruuxee.com -->

# Deploy RuuXee server environment.

This document describes how to deploy ruuxee server environment on a
Linux (for production) or Mac (for development).

## General

Ruuxee project is deployed in a "clean" environment, based on Python
virtualenv tool. We do it to make sure it comes with fixed dependency
list.

Surely developers can choose not to use virtualenv but just directly use
ruuxee module under src/server. However, this is NOT RECOMMENDED in
production environment.

## Deploy environment with script

We use a simple script, ruuxee-deploy.sh, to deploy Ruuxee's virtualenv
environment. You can find it under scripts/ folder. A command
line of ruuxee-deploy.sh looks like below:

    ruuxee-server-deploy.sh <env_root_folder> [pip_dependency_list_file]

Please note that the second parameter is optional. If nothing is
specified, it will use default one, scripts/ruuxee-server-env-deps.txt.

In most environment, developers can choose to use default dependency
list. The second parameter is useful only when developers want to test
a new environment with updated dependency list.
