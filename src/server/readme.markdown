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

#Run unittest
Ruuxee module supports unit tests. It's organized via standard
`unittest` Python module. It's splitted into different groups, defines
under ruuxee/ut/*.py. Developers can run the tests with command line
below:

    python -m unittest ruuxee.ut.creation
    python -m unittest ruuxee.ut.api
