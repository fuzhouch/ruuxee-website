#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

import unittest
import random
import ruuxee.apis.v1.web
import ruuxee.models.v1.mock

class TestApiWithoutAuth(unittest.TestCase):
    def setUp(self):
        self.app = ruuxee.Application('ruuxee.config.webui_dev')
        api_page = ruuxee.apis.v1.web.page
        self.app.register_blueprint(api_page, url_prefix='/apis/v1/web')

    def tearDown(self):
        pass

    def testGetPersonBrief(self):
        with self.app.test_client() as c:
            path = '/apis/v1/web/person-brief'
            dataaccess = self.app.config["RUUXEE_DATA_ACCESS"]
            # Only for fake objects we can get list of persons.
            for each_person in dataaccess.persons():
                visible_id = each_person.visible_id
                resp = c.get('%s/%s' % (path, visible_id))
                self.assertEqual(resp.status_code, ruuxee.httplib.OK)
            # Yes, this is a correct case. Right now webui_dev always
            # return true on authentication, no matter what value is.
            resp = c.get('%s/inavlid_id' % path)
            self.assertEqual(resp.status_code, ruuxee.httplib.OK)

