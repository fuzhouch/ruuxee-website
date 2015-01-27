#Server backend ruuxee README

This folder contains implementation of ruuxee.com backend. It contains
code to manipulate database and represent it via APIs.

##Quick start
To start a server with mock backend for testing, please run command
below:

    python bin/mockserver.py

The command above will start a server running on http://localhost:5000,
and accept requests such as

    GET http://localhost:5000/api/web/v1/person-brief/bourne.zhu
    GET http://localhost:5000/person/bourne.zhu

###Support Web UI developers

The `mockserver.py` script can also be used to support web UI developers
to develop their own web pages, by specifying the developing template. A
command line looks below:

    python bin/mockserver.py --template_folder=../webui/developing

The script will start a test server but point to different template
folder, `../webui/developing`. So other developers can save their own
pages in different places, without mixing server and frontend.

Some notes:

1. Since server end uses [flask](http://flask.pocoo.org/), web UI
   developers have no choice but use [jinjia2](http://jinja.pocoo.org/)
   as template format.

2. The folder of page handling are located under `ruuxee/views/v1/*.py`.

##Run unittest
Ruuxee module supports unit tests. It's organized via standard
`unittest` Python module. It's splitted into different groups, defines
under ruuxee/ut/*.py. Developers can run the tests with command line
below:

    python -m unittest ruuxee.ut.creation
    python -m unittest ruuxee.ut.api
