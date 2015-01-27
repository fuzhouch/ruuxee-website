#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

# Adjust search path to get ruuxee library.
import sys
import os.path
dirname = os.path.dirname(__file__)
search_root = os.path.join(os.getcwd(), dirname)
search_root = os.path.join(search_root, "..")
sys.path.append(search_root)

# Really start server
import ruuxee
import ruuxee.apis.v1.web

app = ruuxee.Application('ruuxee.config.webui_dev')
api_page = ruuxee.apis.v1.web.page
app.register_blueprint(api_page, url_prefix='/api/web/v1')
app.run(debug=True)
