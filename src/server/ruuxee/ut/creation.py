#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

import unittest
import ruuxee.views.timeline

class TestAppCreation(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testCreateApp(self):
        app = ruuxee.Application('ruuxee.config.webui_dev')
        timeline_page = ruuxee.views.timeline.page
        app.register_blueprint(timeline_page)
