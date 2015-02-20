#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

import unittest
import random
import ruuxee.apis.v1.web
import ruuxee.models.v1.mock
import ruuxee.models.v1 as model1
import json
import time
import datetime

class TestApiReturnData(unittest.TestCase):
    def setUp(self):
        self.app = ruuxee.Application('ruuxee.config.webui_dev')
        api_page = ruuxee.apis.v1.web.page
        self.app.register_blueprint(api_page, url_prefix='/apis/web/v1')

        # In test environment, we always authenticate current user
        # as bourne.zhu. so from_name is hard coded.
        self.from_name = "bourne.zhu"
        self.to_name = "fuzhou.chen"

        self.queue = self.app.config["RUUXEE_UT_QUEUE"]
        self.cache = self.app.config["RUUXEE_UT_CACHE"]
        self.database = self.app.config["RUUXEE_UT_DATABASE"]

        self.to_id = self.helper_get_person_visible_id(self.to_name)
        self.from_id = self.helper_get_person_visible_id(self.from_name)
        self.to_obj = None
        self.from_obj = None
        database = self.app.config["RUUXEE_UT_DATABASE"]
        for each_person in database.persons:
            if each_person.readable_id == self.to_name:
                self.to_obj = each_person
            if each_person.readable_id == self.from_name:
                self.from_obj = each_person
        self.from_obj.status = model1.STATUS_ACTIVATED
        self.to_obj.status = model1.STATUS_ACTIVATED



    def tearDown(self):
        pass

    def test_get_person_brief(self):
        with self.app.test_client() as c:
            path = '/apis/web/v1/person-brief'
            dataaccess = self.app.config["RUUXEE_DATA_ACCESS"]
            # Only for fake objects we can get list of persons.
            # Production database may not expose db property.
            for each_person in dataaccess.db.persons:
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
            for each_person in dataaccess.db.persons:
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
            for each_post in dataaccess.db.posts:
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

    def helper_get_person_visible_id(self, readable_id):
        with self.app.test_client() as c:
            path = '/apis/web/v1/person-brief'
            resp = c.get('%s/%s' % (path, readable_id))
            data = json.loads(resp.data)
            visible_id = data["visible_id"]
            return visible_id

    def helper_test_person_post_person_common_invalid(self, path, to_name):
        """
        Test cases
        1. Non-visible ID returns error, BAD_REQUEST
        2. GET/PUT request always return error.
           2.1 GET should return METHOD_NOT_ALLOWED
           2.2 PUT should return METHOD_NOT_ALLOWED
        4. Valid ID with invalid status
           4.1. Non-activated user can't be followed.
           4.2. Non-activated user can't follow anybody
           4.3. A person can't follow himself/herself.
        """
        # Case 1: Invalid IDs are not accepted.
        with self.app.test_client() as c:
            invalid_id = self.to_name
            resp = c.post('%s/%s' % (path, invalid_id)) 
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, ruuxee.httplib.BAD_REQUEST)
            self.assertEqual(len(self.queue.queue), 0)

            invalid_id = str(self.to_id) + "1234"
            resp = c.get('%s/%s' % (path, invalid_id)) 
            self.assertEqual(resp.status_code,
                             ruuxee.httplib.METHOD_NOT_ALLOWED)
            self.assertEqual(len(self.queue.queue), 0)

        # Case 2: GET/PUT methods are not accepted
        with self.app.test_client() as c:
            resp = c.get('%s/%s' % (path, str(self.to_id))) 
            self.assertEqual(resp.status_code,
                             ruuxee.httplib.METHOD_NOT_ALLOWED)
            self.assertEqual(len(self.queue.queue), 0)

            resp = c.put('%s/%s' % (path, str(self.to_id))) 
            self.assertEqual(resp.status_code,
                             ruuxee.httplib.METHOD_NOT_ALLOWED)
            self.assertEqual(len(self.queue.queue), 0)

        # Case 4.1. Non-activated person can't be followed
        original_from_obj_status = self.from_obj.status
        original_to_obj_status = self.to_obj.status
        self.from_obj.status = model1.STATUS_ACTIVATED
        with self.app.test_client() as c:
            for each_status in model1.PENDING_PERSON_STATUS:
                self.to_obj.status = each_status
                resp = c.post('%s/%s' % (path, self.to_id))
                self.assertEqual(resp.status_code,
                                 ruuxee.httplib.METHOD_NOT_ALLOWED)
                self.assertEqual(len(self.queue.queue), 0)

        # Case 4.2. Non-activated person can't follow anybody
        self.to_obj.status = model1.STATUS_ACTIVATED
        with self.app.test_client() as c:
            for each_status in model1.PENDING_PERSON_STATUS:
                self.from_obj.status = each_status
                resp = c.post('%s/%s' % (path, self.to_id))
                self.assertEqual(resp.status_code,
                                 ruuxee.httplib.METHOD_NOT_ALLOWED)
                self.assertEqual(len(self.queue.queue), 0)

        # Case 4.3. A person can't follow himself/herself
        self.from_obj.status = model1.STATUS_ACTIVATED
        with self.app.test_client() as c:
            resp = c.post('%s/%s' % (path, self.from_id))
            self.assertEqual(resp.status_code,
                             ruuxee.httplib.METHOD_NOT_ALLOWED)
            self.assertEqual(len(self.queue.queue), 0)

        # Cleanup: Back to original status
        self.to_obj.status = original_to_obj_status
        self.from_obj.status = original_from_obj_status

    def test_follow_people(self):
        """
        Test cases
        3. A valid ID that was not followed:
           3.1. Get OK.
           3.2. A request is pushed into queue.
           3.3. Command in queue is correct.
           3.4. Timestamp should be valid.

        5. Repeated follow will not take additional processing in
           backend.
        """
        try:
            path = '/apis/web/v1/follow/person'
            fc_name = 'fuzhou.chen'
            self.helper_test_person_post_person_common_invalid(path, fc_name)
        except AssertionError as e:
            # We perform catch and rethrow because we want the error
            # output shows the test function name, instead of helpers.
            raise e

        original_from_obj_status = self.from_obj.status
        original_to_obj_status = self.to_obj.status
        # Case 3
        with self.app.test_client() as c:
            now = int(time.time())
            resp = c.post('%s/%s' % (path, self.to_id))
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, ruuxee.httplib.OK)
            self.assertEqual(len(self.queue.queue), 1)
            command = self.queue.queue.pop()
            splitted = command.split(":")
            calling_dt = int(splitted[0])
            timedelta = calling_dt - now

            self.assertEqual(len(splitted), 5)
            print(timedelta)
            self.assertEqual(timedelta < 1, True)
            self.assertEqual(splitted[1], model1.ACTION_FOLLOW_PERSON)
            self.assertEqual(splitted[2], str(self.from_id))
            self.assertEqual(splitted[3], str(self.to_id))
            self.assertEqual(splitted[4], "")


        # Case 5: Repeated following will return OK but no additional
        # request added to message queue.
        self.from_obj.status = model1.STATUS_ACTIVATED
        self.to_obj.status = model1.STATUS_ACTIVATED
        table = model1.TableNameGenerator.person_follow_person(self.from_id)
        self.cache.insert_set(table, str(self.to_id))
        with self.app.test_client() as c:
            resp = c.post('%s/%s' % (path, self.to_id))
            self.assertEqual(resp.status_code, ruuxee.httplib.OK)
            self.assertEqual(len(self.queue.queue), 0)
        # Cleanup: Back to original status
        self.cache.remove_set(table, str(self.to_id))
        self.to_obj.status = original_to_obj_status
        self.from_obj.status = original_from_obj_status

    def test_unfollow_people(self):
        """
        Test cases
        3. A valid ID that was already followed:
           3.1. Get OK.
           3.2. A request is pushed into queue.
           3.3. Command in queue is correct.
           3.4. Timestamp should be valid.

        5. Repeated unfollow will not take additional processing in
           backend.
        """
        try:
            path = '/apis/web/v1/unfollow/person'
            fc_name = 'fuzhou.chen'
            self.helper_test_person_post_person_common_invalid(path, fc_name)
        except AssertionError as e:
            # We perform catch and rethrow because we want the error
            # output shows the test function name, instead of helpers.
            raise e

        original_from_obj_status = self.from_obj.status
        original_to_obj_status = self.to_obj.status
        # Case 3
        self.from_obj.status = model1.STATUS_ACTIVATED
        self.to_obj.status = model1.STATUS_ACTIVATED
        table = model1.TableNameGenerator.person_follow_person(self.from_id)
        self.cache.insert_set(table, str(self.to_id))
        with self.app.test_client() as c:
            now = int(time.time())
            resp = c.post('%s/%s' % (path, self.to_id))
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, ruuxee.httplib.OK)
            self.assertEqual(len(self.queue.queue), 1)
            command = self.queue.queue.pop()
            splitted = command.split(":")
            calling_dt = int(splitted[0])
            timedelta = calling_dt - now

            self.assertEqual(len(splitted), 5)
            print(timedelta)
            self.assertEqual(timedelta < 1, True)
            self.assertEqual(splitted[1], model1.ACTION_UNFOLLOW_PERSON)
            self.assertEqual(splitted[2], str(self.from_id))
            self.assertEqual(splitted[3], str(self.to_id))
            self.assertEqual(splitted[4], "")
        # Cleanup: Back to original status
        self.cache.remove_set(table, str(self.to_id))

        # Case 5: Repeated following will return OK but no additional
        # request added to message queue.
        with self.app.test_client() as c:
            resp = c.post('%s/%s' % (path, self.to_id))
            self.assertEqual(resp.status_code, ruuxee.httplib.OK)
            self.assertEqual(len(self.queue.queue), 0)
        # Cleanup: Back to original status
        self.to_obj.status = original_to_obj_status
        self.from_obj.status = original_from_obj_status

