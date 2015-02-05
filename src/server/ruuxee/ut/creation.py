#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

import unittest
import random
import ruuxee.views.timeline
import ruuxee.models.v1.mock

class TestAppCreation(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testCreateApp(self):
        app = ruuxee.Application('ruuxee.config.webui_dev')
        timeline_page = ruuxee.views.timeline.page
        app.register_blueprint(timeline_page)

class TestMockDatabase(unittest.TestCase):
    def setUp(self):
        random.seed()
    def testCreateMockDb(self):
        cache = ruuxee.models.v1.mock.Cache()
        db = ruuxee.models.v1.mock.Database(cache)
