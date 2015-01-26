#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"Main module to start ruuxee."

__version__ = "0.1.0.0"

import flask
import sys
if sys.version_info.major >= 3:
    import http.client as httplib
else:
    import httplib

APP_NAME = 'ruuxee' # Hardcoded package name. Don't change.

class Application(flask.Flask):
    "Toplevel flask application generator."
    def __init__(self, config):
        """Application.__init__(self, config)

        Extends flask.Flask for a unified configuration.
        """
        self.__app_name = APP_NAME # Flask modules require hardcoded name
        flask.Flask.__init__(self, self.__app_name)
        self.config.from_object(config)
    def app_name(self):
        return self.__app_name

class View(flask.Blueprint):
    "Toplevel view generator, based on :object:flask.Blueprint."
    def __init__(self, view_name):
        # Make sure all views share the same inherited folder structure.
        self.__app_name = APP_NAME
        flask.Blueprint.__init__(self, view_name, self.__app_name)
