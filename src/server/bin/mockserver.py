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
                    level=logging.INFO)

import ruuxee
import ruuxee.apis.v1.web
import ruuxee.models.v1
import ruuxee.views.person
import threading
import signal

class TestServer(object):
    def __init__(self):
        # Configure app
        self.app = ruuxee.Application(config='ruuxee.config.webui_dev',
                                      template_folder=args.template_folder)
        self.api_page = ruuxee.apis.v1.web.page
        self.person_page = ruuxee.views.person.page
        self.app.register_blueprint(self.api_page, url_prefix='/api/web/v1')
        self.app.register_blueprint(self.person_page, url_prefix='/person')
        # Start a backend processor to handle all requests pushed to
        # message queue.
        self.queue = self.app.config["RUUXEE_UT_QUEUE"]
        self.cache = self.app.config["RUUXEE_UT_CACHE"]
        self.database = self.app.config["RUUXEE_UT_DATABASE"]
        self.queue.set_with_worker(True)
        self.worker = ruuxee.models.v1.RequestWorker(self.database,
                                                     self.cache,
                                                     self.queue)
        self.worker_thread = threading.Thread(target=self.worker.main_loop)

        # Install signal handler to gracefully exit.
        self.__prev_on_exit = signal.signal(signal.SIGINT, self.__on_exit)

    def __on_exit(self, signum, frame):
        logging.info("Gracefully exit current main loop.")
        self.queue.push_queue(ruuxee.models.v1.MESSAGE_QUEUE_STOP_SIGN)
        self.worker_thread.join()
        if self.__prev_on_exit:
            return self.__prev_on_exit(signum, frame)
        return 0

    def run(self):
        self.worker_thread.start()
        self.app.run(debug=True)
        self.queue.push_queue(ruuxee.models.v1.MESSAGE_QUEUE_STOP_SIGN)
        self.worker_thread.join()

# OK. Now start service
if __name__ == '__main__':
    TestServer().run()
