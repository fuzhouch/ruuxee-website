#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

# Adjust search path to get ruuxee library.
import sys
import os.path
import argparse
import logging

dirname = os.path.dirname(__file__)
search_root = os.path.join(os.getcwd(), dirname)
search_root = os.path.join(search_root, "..")
sys.path.append(search_root)

parser = argparse.ArgumentParser(description="Start a mock server.")
parser.add_argument('-t',
                    '--template_folder',
                    dest='template_folder',
                    default=None,
                    help='Specify the HTML template folder.')
parser.add_argument('-l',
                    '--log',
                    dest='log',
                    default="mockserver.log",
                    help='Specify log file for debugging.')

try:
    args = parser.parse_args()
except Exception:
    parser.print_help()
    sys.exit(1)

formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=args.log, \
                    format=formatter, \
                    level=logging.DEBUG)

import ruuxee
import ruuxee.apis.v1.web
import ruuxee.views.person

app = ruuxee.Application(config='ruuxee.config.webui_dev',
                         template_folder=args.template_folder)
api_page = ruuxee.apis.v1.web.page
person_page = ruuxee.views.person.page
app.register_blueprint(api_page, url_prefix='/api/web/v1')
app.register_blueprint(person_page, url_prefix='/person')
app.run(debug=True)
