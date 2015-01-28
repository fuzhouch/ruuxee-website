#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

import unittest
import random
import ruuxee.apis.v1.web
import ruuxee.models.v1.mock
import json

class TestApiReturnData(unittest.TestCase):
    def setUp(self):
        self.app = ruuxee.Application('ruuxee.config.webui_dev')
        api_page = ruuxee.apis.v1.web.page
        self.app.register_blueprint(api_page, url_prefix='/apis/web/v1')

    def tearDown(self):
        pass

    def test_get_person_brief(self):
        with self.app.test_client() as c:
            path = '/apis/web/v1/person-brief'
            dataaccess = self.app.config["RUUXEE_DATA_ACCESS"]
            # Only for fake objects we can get list of persons.
            # Production database may not expose db property.
            for each_person in dataaccess.db.persons():
                visible_id = each_person.visible_id
                resp = c.get('%s/%s' % (path, visible_id))
                self.assertEqual(resp.status_code, ruuxee.httplib.OK)
                self.assertEqual(resp.content_encoding, 'utf-8')
                data = json.loads(resp.data)
                self.assertEqual(data['name'], each_person.name)
                self.assertEqual(data['company'], each_person.company)
                self.assertEqual(data['visible_id'],
                                 each_person.visible_id)
                self.assertEqual(data['readable_id'],
                                 each_person.readable_id)
                self.assertEqual(len(data), 5)
            for each_person in dataaccess.db.persons():
                readable_id = each_person.readable_id
                resp = c.get('%s/%s' % (path, readable_id))
                self.assertEqual(resp.status_code, ruuxee.httplib.OK)
                self.assertEqual(resp.content_encoding, 'utf-8')
                self.assertEqual(resp.headers["Content-Encoding"], 'utf-8')
                data = json.loads(resp.data)
                self.assertEqual(data['name'], each_person.name)
                self.assertEqual(data['company'], each_person.company)
                self.assertEqual(data['visible_id'],
                                 each_person.visible_id)
                self.assertEqual(data['readable_id'],
                                 each_person.readable_id)
                self.assertEqual(data["status_code"], ruuxee.httplib.OK)
                self.assertEqual(len(data), 5)


            resp = c.get('%s/inavlid_id' % path)
            self.assertEqual(resp.status_code, ruuxee.httplib.BAD_REQUEST)

    def test_get_post_brief(self):
        with self.app.test_client() as c:
            path = '/apis/web/v1/post-brief'
            dataaccess = self.app.config["RUUXEE_DATA_ACCESS"]
            # Only for fake objects we can get list of persons.
            # Production database may not expose db property.
            for each_post in dataaccess.db.posts():
                visible_id = each_post.visible_id
                resp = c.get('%s/%s' % (path, visible_id))
                self.assertEqual(resp.status_code, ruuxee.httplib.OK)
                data = json.loads(resp.data)
                self.assertEqual(data["status_code"], ruuxee.httplib.OK)
                status = data["status"]

                if status == ruuxee.models.v1.POST_STATUS_POSTED:
                    # Reviewing posts:
                    # 1. The title and contents are hidden.
                    # 2. Author name can be shown or hidden
                    self.assertEqual(data["brief_text"], \
                                     each_post.brief_text)
                    self.assertEqual(data["title"], each_post.title)
                    self.assertEqual(data["brief_text"], \
                                     each_post.brief_text)
                    if data["is_anonymous"]:
                        self.assertEqual(data["author_name"], \
                                 ruuxee.models.v1.ANONYMOUS_PERSON_NAME)
                    else:
                        self.assertEqual("author_name" in data, True)
                        # Author name is kinds of complicated. The
                        # returned object contains only author_name. We
                        # must map it to real name.
                        found = dataaccess.db.query_person('visible_id',\
                                            each_post.author_visible_id,\
                                                           ['name'])
                        self.assertEqual(found != None, True)
                        self.assertEqual(found[0]["name"],\
                                         data["author_name"])

                    self.assertEqual(len(data), 6)
                elif status == ruuxee.models.v1.POST_STATUS_REVIWING:
                    # Reviewing posts:
                    # 1. The title and contents are hidden.
                    # 2. Author name can be shown or hidden
                    self.assertEqual(data["brief_text"], \
                                     ruuxee.models.v1.REVIEWING_TEXT)
                    self.assertEqual(data["title"], \
                                     ruuxee.models.v1.REVIEWING_TITLE)
                    self.assertEqual("author_name" in data, True)
                    if data["is_anonymous"]:
                        self.assertEqual(data["author_name"], \
                                 ruuxee.models.v1.ANONYMOUS_PERSON_NAME)
                    else:
                        self.assertEqual("author_name" in data, True)
                        # Author name is kinds of complicated. The
                        # returned object contains only author_name. We
                        # must map it to real name.
                        found = dataaccess.db.query_person('visible_id',\
                                            each_post.author_visible_id,\
                                                           ['name'])
                        self.assertEqual(found != None, True)
                        self.assertEqual(found[0]["name"],\
                                         data["author_name"])

                    self.assertEqual(len(data), 6)
                elif status == ruuxee.models.v1.POST_STATUS_DELETED:
                    self.assertEqual(len(data), 2)
                else:
                    # Impossible to reach here.
                    self.assertEqual(True, False)

            resp = c.get('%s/inavlid_id' % path)
            self.assertEqual(resp.status_code, ruuxee.httplib.BAD_REQUEST)
