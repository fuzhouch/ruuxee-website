#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

import unittest
import random
import ruuxee.apis.v1.web
import ruuxee.models.v1.mock
import ruuxee.models.v1 as model1
import ruuxee.utils as utils
import json
import time
import datetime
import traceback
import sys
import threading

class BaseEnvironment(unittest.TestCase):
    "A helper class to provide common functions for testing."
    def helper_wait_queue_empty(self, wait_max_secs = 0):
        wait_count = 0
        while len(self.queue.queue) != 0:
            time.sleep(0.5)
            wait_count += 0.5
            if wait_max_secs > 0 and wait_count > wait_max_secs:
                return False
        return True

    def setUp(self):
        self.app = ruuxee.Application('ruuxee.config.unittest')
        api_page = ruuxee.apis.v1.web.page
        self.app.register_blueprint(api_page, url_prefix='/apis/web/v1')

        self.queue = self.app.config["RUUXEE_UT_QUEUE"]
        self.cache = self.app.config["RUUXEE_UT_CACHE"]
        self.database = self.app.config["RUUXEE_UT_DATABASE"]

        # In test environment, we always authenticate current user
        # as bourne.zhu. so from_name is hard coded.
        #
        # Meanwhile, we want a guy with at least a post. However we
        # can't guarantee all person have posts, so we have to pick a
        # post and select its writer as target person.
        self.from_person_name = "bourne.zhu"
        self.from_person = self.helper_get_person(self.from_person_name)
        self.from_person_id = self.from_person.visible_id
        self.from_person.status = model1.STATUS_ACTIVATED

        self.from_post = self.database.posts[0]
        self.from_post.status = model1.STATUS_ACTIVATED
        self.from_post_id = self.from_post.visible_id

        # Let's pick the first article not written by bourne.zhu.
        self.to_post = None
        for each_post in self.database.posts:
            if each_post.author_visible_id != self.from_person_id:
                self.to_post = each_post
                self.to_post.status = model1.STATUS_ACTIVATED
                self.to_post_id = self.to_post.visible_id
                break
        assert self.to_post is not None

        # Then the writer as target user.
        self.to_person = None
        for each_person in self.database.persons:
            if each_person.visible_id == self.to_post.author_visible_id:
                self.to_person = each_person
                break
        self.to_person_id = self.to_person.visible_id
        self.to_person.status = model1.STATUS_ACTIVATED
        assert self.to_person is not None

        self.to_topic = self.database.topics[0]
        self.to_topic_id = self.to_topic.visible_id
        self.to_topic.status = model1.STATUS_ACTIVATED

    def tearDown(self):
        pass

    def helper_empty_queue(self):
        for i in range(len(self.queue.queue)):
            self.queue.pop_queue()

    def helper_get_person(self, readable_id):
        database = self.app.config["RUUXEE_UT_DATABASE"]
        for each_person in database.persons:
            if each_person.readable_id == readable_id:
                return each_person
        return None

    def helper_post(self, path, status_code = ruuxee.httplib.OK):
        with self.app.test_client() as c:
            resp = c.post('%s' % path)
            self.assertEqual(resp.status_code, status_code)
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, status_code)
            return resp

    def helper_get(self, path, return_val = ruuxee.httplib.OK):
        with self.app.test_client() as c:
            resp = c.get('%s' % path)
            self.assertEqual(resp.status_code, return_val)
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, return_val)
            return resp

    def helper_post_message(self, action, source, target, addition):
        ts = utils.stimestamp()
        record = "%d:%s:%s:%s:%s" % (ts, action, source, target, addition)
        self.queue.push_queue(record)

class TestApiReturnData(BaseEnvironment):
    def test_get_person_brief(self):
        with self.app.test_client() as c:
            path = '/apis/web/v1/person-brief'
            core = self.app.config["RUUXEE_CORE"]
            # Only for fake objects we can get list of persons.
            # Production database may not expose db property.
            for each_person in core.db.persons:
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
            for each_person in core.db.persons:
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

    def test_get_topic_brief(self):
        with self.app.test_client() as c:
            path = '/apis/web/v1/topic-brief'
            core = self.app.config["RUUXEE_CORE"]
            # Only for fake objects we can get list of persons.
            # Production database may not expose db property.
            for each_topic in core.db.topics:
                visible_id = each_topic.visible_id
                resp = c.get('%s/%s' % (path, visible_id))
                self.assertEqual(resp.status_code, ruuxee.httplib.OK)
                self.assertEqual(resp.content_encoding, 'utf-8')
                data = json.loads(resp.data)
                self.assertEqual(data['title'], each_topic.title)
                self.assertEqual(data['description'], each_topic.description)
                self.assertEqual(data['visible_id'], each_topic.visible_id)
                self.assertEqual(data["status_code"], ruuxee.httplib.OK)
                self.assertEqual(len(data), 4)
            resp = c.get('%s/inavlid_id' % path)
            self.assertEqual(resp.status_code, ruuxee.httplib.BAD_REQUEST)

    def test_get_post_brief(self):
        with self.app.test_client() as c:
            path = '/apis/web/v1/post-brief'
            core = self.app.config["RUUXEE_CORE"]
            # Only for fake objects we can get list of persons.
            # Production database may not expose db property.
            for each_post in core.db.posts:
                visible_id = each_post.visible_id
                resp = c.get('%s/%s' % (path, visible_id))
                self.assertEqual(resp.status_code, ruuxee.httplib.OK)
                data = json.loads(resp.data)
                self.assertEqual(data["status_code"], ruuxee.httplib.OK)
                status = data["status"]

                if status == ruuxee.models.v1.STATUS_ACTIVATED:
                    # Reviewing posts:
                    # 1. The title and contents are hidden.
                    # 2. Author name can be shown or hidden
                    self.assertEqual(data["brief_text"], \
                                     each_post.brief_text)
                    self.assertEqual(data["title"], each_post.title)
                    self.assertEqual(data["brief_text"], \
                                     each_post.brief_text)
                    self.assertEqual("author_name" in data, True)
                    self.assertEqual("visible_id" in data, True)
                    self.assertEqual(data["visible_id"], visible_id)
                    if data["is_anonymous"]:
                        self.assertEqual(data["author_name"], \
                                 ruuxee.models.v1.ANONYMOUS_PERSON_NAME)
                        self.assertEqual("author_visible_id" in data, False)
                        self.assertEqual("author_readable_id" in data, False)
                        self.assertEqual(len(data), 7)
                    else:
                        self.assertEqual("author_visible_id" in data, True)
                        self.assertEqual("author_readable_id" in data, True)
                        # Author name is kinds of complicated. The
                        # returned object contains only author_name. We
                        # must map it to real name.
                        found = core.db.query_person('visible_id',\
                                            each_post.author_visible_id,\
                                                           ['name'])
                        self.assertEqual(found != None, True)
                        self.assertEqual(found[0]["name"],\
                                         data["author_name"])
                        self.assertEqual(len(data), 9)
                elif status == ruuxee.models.v1.STATUS_REVIEWING:
                    # Reviewing posts:
                    # 1. The title and contents are hidden.
                    # 2. Author name can be shown or hidden
                    self.assertEqual(data["brief_text"], \
                                     ruuxee.models.v1.REVIEWING_TEXT)
                    self.assertEqual(data["title"], \
                                     ruuxee.models.v1.REVIEWING_TITLE)
                    self.assertEqual("author_name" in data, True)
                    self.assertEqual("visible_id" in data, True)
                    self.assertEqual(data["visible_id"], visible_id)
                    if data["is_anonymous"]:
                        self.assertEqual(data["author_name"], \
                                 ruuxee.models.v1.ANONYMOUS_PERSON_NAME)
                        self.assertEqual("author_visible_id" in data, False)
                        self.assertEqual("author_readable_id" in data, False)
                        self.assertEqual(len(data), 7)
                    else:
                        self.assertEqual("author_visible_id" in data, True)
                        self.assertEqual("author_readable_id" in data, True)
                        # Author name is kinds of complicated. The
                        # returned object contains only author_name. We
                        # must map it to real name.
                        found = core.db.query_person('visible_id',\
                                            each_post.author_visible_id,\
                                                           ['name'])
                        self.assertEqual(found != None, True)
                        self.assertEqual(found[0]["name"],\
                                         data["author_name"])
                        self.assertEqual(len(data), 9)
                elif status == ruuxee.models.v1.STATUS_SUSPENDED:
                    # Suspended posts:
                    # 1. The title and contents are hidden.
                    # 2. Author name can be shown or hidden
                    self.assertEqual(data["brief_text"], \
                                     ruuxee.models.v1.SUSPENDED_TEXT)
                    self.assertEqual(data["title"], \
                                     ruuxee.models.v1.SUSPENDED_TITLE)
                    self.assertEqual("author_name" in data, True)
                    self.assertEqual("visible_id" in data, True)
                    self.assertEqual(data["visible_id"], visible_id)
                    if data["is_anonymous"]:
                        self.assertEqual(data["author_name"], \
                                 ruuxee.models.v1.ANONYMOUS_PERSON_NAME)
                        self.assertEqual("author_visible_id" in data, False)
                        self.assertEqual("author_readable_id" in data, False)
                        self.assertEqual(len(data), 7)
                    else:
                        self.assertEqual("author_visible_id" in data, True)
                        self.assertEqual("author_readable_id" in data, True)
                        # Author name is kinds of complicated. The
                        # returned object contains only author_name. We
                        # must map it to real name.
                        found = core.db.query_person('visible_id',\
                                    each_post.author_visible_id, ['name'])
                        self.assertEqual(found != None, True)
                        self.assertEqual(found[0]["name"], data["author_name"])
                        self.assertEqual(len(data), 9)
                elif status == ruuxee.models.v1.STATUS_DELETED:
                    self.assertEqual(len(data), 2)
                else:
                    # Impossible to reach here.
                    self.assertEqual(True, False)

            resp = c.get('%s/inavlid_id' % path)
            self.assertEqual(resp.status_code, ruuxee.httplib.BAD_REQUEST)

    def helper_test_common(self, path, from_obj, to_obj):
        """
        Test cases
        1. Non-visible ID returns error, NOT_FOUND
        2. GET/PUT request always return error.
           2.1 GET should return METHOD_NOT_ALLOWED
           2.2 PUT should return METHOD_NOT_ALLOWED
        4. Valid ID with invalid status
           4.1. Non-activated user can't be followed.
           4.2. Non-activated user can't follow anybody
           4.3. A person can't follow himself/herself.
        """
        self.helper_empty_queue()
        from_visible_id = from_obj.visible_id
        to_visible_id = to_obj.visible_id

        # Case 1: Invalid IDs are not accepted.
        with self.app.test_client() as c:
            invalid_id = "1q2w3e4r"
            resp = c.post('%s/%s' % (path, invalid_id)) 
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, ruuxee.httplib.NOT_FOUND)
            self.assertEqual(len(self.queue.queue), 0)

            invalid_id = to_visible_id + "1234"
            resp = c.get('%s/%s' % (path, invalid_id)) 
            self.assertEqual(resp.status_code,
                             ruuxee.httplib.METHOD_NOT_ALLOWED)
            self.assertEqual(len(self.queue.queue), 0)

        # Case 2: GET/PUT methods are not accepted
        with self.app.test_client() as c:
            resp = c.get('%s/%s' % (path, to_visible_id)) 
            self.assertEqual(resp.status_code,
                             ruuxee.httplib.METHOD_NOT_ALLOWED)
            self.assertEqual(len(self.queue.queue), 0)

            resp = c.put('%s/%s' % (path, to_visible_id)) 
            self.assertEqual(resp.status_code,
                             ruuxee.httplib.METHOD_NOT_ALLOWED)
            self.assertEqual(len(self.queue.queue), 0)

        # Case 4.1. Non-activated person can't be followed
        original_from_obj_status = from_obj.status
        original_to_obj_status = to_obj.status
        from_obj.status = model1.STATUS_ACTIVATED
        with self.app.test_client() as c:
            for each_status in model1.PENDING_STATUS:
                to_obj.status = each_status
                resp = c.post('%s/%s' % (path, to_visible_id))
                self.assertEqual(resp.status_code,
                                 ruuxee.httplib.METHOD_NOT_ALLOWED)
                self.assertEqual(len(self.queue.queue), 0)

        # Case 4.2. Non-activated person can't follow anybody
        to_obj.status = model1.STATUS_ACTIVATED
        with self.app.test_client() as c:
            for each_status in model1.PENDING_STATUS:
                from_obj.status = each_status
                resp = c.post('%s/%s' % (path, to_visible_id))
                self.assertEqual(resp.status_code,
                                 ruuxee.httplib.METHOD_NOT_ALLOWED)
                self.assertEqual(len(self.queue.queue), 0)

        # Cleanup: Back to original status
        to_obj.status = original_to_obj_status
        from_obj.status = original_from_obj_status

    def helper_test_person_self(self, path, from_obj, to_obj):
        # Case 4.3. A person can't follow himself/herself
        original_from_obj_status = from_obj.status
        from_obj.status = model1.STATUS_ACTIVATED
        with self.app.test_client() as c:
            resp = c.post('%s/%s' % (path, str(from_obj.visible_id)))
            self.assertEqual(resp.status_code,
                             ruuxee.httplib.METHOD_NOT_ALLOWED)
            self.assertEqual(len(self.queue.queue), 0)
        from_obj.status = original_from_obj_status

    def helper_test_self_post(self, path):
        with self.app.test_client() as c:
            resp = c.post('%s/%s' % (path, self.from_post_id))
            self.assertEqual(resp.status_code,
                             ruuxee.httplib.METHOD_NOT_ALLOWED)
            self.assertEqual(len(self.queue.queue), 0)

    def helper_test_valid(self, path, command_id, to_obj):
        pid = to_obj.visible_id
        with self.app.test_client() as c:
            now = int(time.time())
            resp = c.post('%s/%s' % (path, to_obj.visible_id))
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, ruuxee.httplib.OK)
            self.assertEqual(len(self.queue.queue), 1)
            command = self.queue.queue.pop()
            splitted = command.split(":")
            calling_dt = int(splitted[0])
            timedelta = calling_dt - now

            self.assertEqual(len(splitted), 5)
            self.assertEqual(timedelta < 1, True)
            self.assertEqual(splitted[1], command_id)
            self.assertEqual(splitted[2], self.from_person_id)
            self.assertEqual(splitted[3], to_obj.visible_id)
            self.assertEqual(splitted[4], "")
        # Case 3: Repeated request can still return
        with self.app.test_client() as c:
            now = int(time.time())
            resp = c.post('%s/%s' % (path, to_obj.visible_id))
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, ruuxee.httplib.OK)
            # Repeat once
            resp = c.post('%s/%s' % (path, to_obj.visible_id))
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, ruuxee.httplib.OK)
            # Now there should be two items in queue.
            self.assertEqual(len(self.queue.queue), 2)
        self.queue.queue.pop()
        self.queue.queue.pop()

    def test_upvote_post(self):
        """
        Test case
        1. A valid ID was neutral:
           1.1 Get OK.
           1.2 A request is pushed into queue.
           1.3 Command in queue is correct.
           1.4 Timestamp should be valid.

        2. Can't upvote owned by current user.
        3. Repeated upvote will take additional processing in backend.
        """
        self.helper_empty_queue()
        path = '/apis/web/v1/upvote/post'
        self.helper_test_common(path, self.from_person, self.to_post)
        # Case 2
        self.helper_test_self_post(path)
        # Case 1 and Case 3
        pid = self.to_post_id
        upvote_table = model1.TableNameGenerator.post_upvote(pid)
        downvote_table = model1.TableNameGenerator.post_downvote(pid)
        self.cache.initialize_list(upvote_table)
        self.cache.initialize_list(downvote_table)
        self.helper_test_valid(path, model1.ACTION_UPVOTE_POST,
                               self.to_post)

    def test_downvote_post(self):
        """
        Test case
        1. A valid ID was neutral:
           1.1 Get OK.
           1.2 A request is pushed into queue.
           1.3 Command in queue is correct.
           1.4 Timestamp should be valid.

        2. Can't downvote owned by current user.
        3. Repeated downvote will take additional processing in backend.
        """
        self.helper_empty_queue()
        path = '/apis/web/v1/downvote/post'
        self.helper_test_common(path, self.from_person, self.to_post)
        # Case 2
        self.helper_test_self_post(path)
        # Case 1 and Case 3
        pid = self.to_post_id
        upvote_table = model1.TableNameGenerator.post_upvote(pid)
        downvote_table = model1.TableNameGenerator.post_downvote(pid)
        self.cache.initialize_list(upvote_table)
        self.cache.initialize_list(downvote_table)
        self.helper_test_valid(path, model1.ACTION_DOWNVOTE_POST,\
                               self.to_post)

    def test_neutralize_post(self):
        """
        Test case
        1. A valid ID was neutral:
           1.1 Get OK.
           1.2 A request is pushed into queue.
           1.3 Command in queue is correct.
           1.4 Timestamp should be valid.

        2. Can't neutralize owned by current user.
        3. Repeated neutralize will take additional processing in backend.
        """
        self.helper_empty_queue()
        path = '/apis/web/v1/neutralize/post'
        self.helper_test_common(path, self.from_person, self.to_post)
        # Case 2
        self.helper_test_self_post(path)
        # Case 1 and Case 3
        pid = self.to_post_id
        upvote_table = model1.TableNameGenerator.post_upvote(pid)
        downvote_table = model1.TableNameGenerator.post_downvote(pid)
        self.cache.initialize_list(upvote_table)
        self.cache.initialize_list(downvote_table)
        self.helper_test_valid(path, model1.ACTION_NEUTRALIZE_POST,\
                               self.to_post)


    def test_follow_people(self):
        """
        Test cases
        3. A valid ID that was not followed:
           3.1 Get OK.
           3.2 A request is pushed into queue.
           3.3 Command in queue is correct.
           3.4 Timestamp should be valid.

        5. Repeated follow will take additional processing in backend.
        """
        self.helper_empty_queue()
        path = '/apis/web/v1/follow/person'
        self.helper_test_common(path, self.from_person, self.to_person)
        self.helper_test_person_self(path, self.from_person, self.to_person)

        original_from_obj_status = self.from_person.status
        original_to_obj_status = self.to_person.status
        # Case 3
        with self.app.test_client() as c:
            now = int(time.time())
            resp = c.post('%s/%s' % (path, self.to_person.visible_id))
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, ruuxee.httplib.OK)
            self.assertEqual(len(self.queue.queue), 1)
            command = self.queue.queue.pop()
            splitted = command.split(":")
            calling_dt = int(splitted[0])
            timedelta = calling_dt - now

            self.assertEqual(len(splitted), 5)
            self.assertEqual(timedelta < 1, True)
            self.assertEqual(splitted[1], model1.ACTION_FOLLOW_PERSON)
            self.assertEqual(splitted[2], str(self.from_person_id))
            self.assertEqual(splitted[3], str(self.to_person_id))
            self.assertEqual(splitted[4], "")

        # Case 5: Repeated following will return OK and an additional
        # request added to message queue.
        self.from_person.status = model1.STATUS_ACTIVATED
        self.to_person.status = model1.STATUS_ACTIVATED
        fid = self.from_person_id
        table = model1.TableNameGenerator.person_follow_person(fid)
        self.cache.insert_set(table, str(self.to_person_id))
        with self.app.test_client() as c:
            resp = c.post('%s/%s' % (path, self.to_person_id))
            self.assertEqual(resp.status_code, ruuxee.httplib.OK)
            resp = c.post('%s/%s' % (path, self.to_person_id))
            self.assertEqual(resp.status_code, ruuxee.httplib.OK)
            self.assertEqual(len(self.queue.queue), 2)
        self.queue.queue.pop()
        self.queue.queue.pop()


        # Cleanup: Back to original status
        self.cache.remove_set(table, str(self.to_person_id))
        self.to_person.status = original_to_obj_status
        self.from_person.status = original_from_obj_status

    def test_unfollow_people(self):
        """
        Test cases
        3. A valid ID that was already followed:
           3.1. Get OK.
           3.2. A request is pushed into queue.
           3.3. Command in queue is correct.
           3.4. Timestamp should be valid.

        5. Repeated unfollow will take additional processing in
           backend.
        """
        self.helper_empty_queue()
        path = '/apis/web/v1/unfollow/person'
        self.helper_test_common(path, self.from_person, self.to_person)
        self.helper_test_person_self(path, self.from_person, self.to_person)
        original_from_obj_status = self.from_person.status
        original_to_obj_status = self.to_person.status
        # Case 3
        self.from_person.status = model1.STATUS_ACTIVATED
        self.to_person.status = model1.STATUS_ACTIVATED
        fid = self.from_person_id
        table = model1.TableNameGenerator.person_follow_person(fid)
        self.cache.insert_set(table, str(self.to_person_id))
        with self.app.test_client() as c:
            now = int(time.time())
            resp = c.post('%s/%s' % (path, self.to_person_id))
            data = json.loads(resp.data)
            status_code = data["status_code"]
            self.assertEqual(status_code, ruuxee.httplib.OK)
            self.assertEqual(len(self.queue.queue), 1)
            command = self.queue.queue.pop()
            splitted = command.split(":")
            calling_dt = int(splitted[0])
            timedelta = calling_dt - now

            self.assertEqual(len(splitted), 5)
            self.assertEqual(timedelta < 1, True)
            self.assertEqual(splitted[1], model1.ACTION_UNFOLLOW_PERSON)
            self.assertEqual(splitted[2], self.from_person_id)
            self.assertEqual(splitted[3], self.to_person_id)
            self.assertEqual(splitted[4], "")
        # Cleanup: Back to original status
        self.cache.remove_set(table, self.to_person_id)

        # Case 5: Repeated following will return OK and an additional
        # request added to message queue.
        with self.app.test_client() as c:
            resp = c.post('%s/%s' % (path, self.to_person_id))
            self.assertEqual(resp.status_code, ruuxee.httplib.OK)
            resp = c.post('%s/%s' % (path, self.to_person_id))
            self.assertEqual(resp.status_code, ruuxee.httplib.OK)
            self.assertEqual(len(self.queue.queue), 2)
        self.queue.queue.pop()
        self.queue.queue.pop()

        # Cleanup: Back to original status
        self.to_person.status = original_to_obj_status
        self.from_person.status = original_from_obj_status

    def test_unfollow_topic(self):
        """
        Test cases
        3. A valid ID that was already followed:
           3.1. Get OK.
           3.2. A request is pushed into queue.
           3.3. Command in queue is correct.
           3.4. Timestamp should be valid.

        5. Repeated unfollow will take additional processing in
           backend.
        """
        self.helper_empty_queue()
        path = '/apis/web/v1/unfollow/topic'
        self.helper_test_common(path, self.from_person, self.to_topic)

        tid = self.to_topic.visible_id
        follow_table = model1.TableNameGenerator.person_follow_topic(tid)
        self.cache.initialize_list(follow_table)
        self.helper_test_valid(path, model1.ACTION_UNFOLLOW_TOPIC,\
                               self.to_topic)

    def test_follow_topic(self):
        """
        Test cases
        3. A valid ID that was already followed:
           3.1. Get OK.
           3.2. A request is pushed into queue.
           3.3. Command in queue is correct.
           3.4. Timestamp should be valid.

        5. Repeated unfollow will take additional processing in
           backend.
        """
        self.helper_empty_queue()
        path = '/apis/web/v1/follow/topic'
        self.helper_test_common(path, self.from_person, self.to_topic)

        tid = self.to_topic.visible_id
        follow_table = model1.TableNameGenerator.person_follow_topic(tid)
        self.cache.initialize_list(follow_table)
        self.helper_test_valid(path, model1.ACTION_FOLLOW_TOPIC,\
                               self.to_topic)


class TestEndToEndWithMockDb(BaseEnvironment):
    def setUp(self):
        BaseEnvironment.setUp(self)
        # We use a background service
        self.queue.set_with_worker(True)
        self.worker = model1.RequestWorker(self.database, self.cache,\
                                           self.queue)
        self.processor = threading.Thread(target=self.worker.main_loop)
        self.processor.start()

        # Helper data for testing notifications
        self.actions_in_notification = [
                model1.ACTION_UPVOTE_POST,
                model1.ACTION_FOLLOW_PERSON
                ]
        # TODO Will be updated when supporting adding
        # post/topic/comments. See ruuxee.model.v1.ALL_NOTIFICATION_ACTIONS

        self.source_target_in_notification = {
                model1.ACTION_UPVOTE_POST: [\
                        self.to_person_id, self.from_post_id],
                model1.ACTION_FOLLOW_PERSON: [\
                        self.to_person_id, self.from_person_id],
                }

        self.actions_out_of_notification = [
                model1.ACTION_DOWNVOTE_POST,
                model1.ACTION_NEUTRALIZE_POST,
                model1.ACTION_UNFOLLOW_PERSON,
                model1.ACTION_FOLLOW_TOPIC,
                model1.ACTION_UNFOLLOW_TOPIC
                ]

        self.source_target_out_of_notification = {
                model1.ACTION_DOWNVOTE_POST: [\
                        self.to_person_id, self.from_post_id],
                model1.ACTION_NEUTRALIZE_POST: [\
                        self.to_person_id, self.from_post_id],
                model1.ACTION_UNFOLLOW_PERSON: [\
                        self.to_person_id, self.from_person_id],
                model1.ACTION_FOLLOW_TOPIC: [\
                        self.to_person_id, self.to_topic_id],
                model1.ACTION_UNFOLLOW_TOPIC: [\
                        self.to_person_id, self.to_topic_id],
                }

        # Helper data for testing timeline.
        self.actions_in_timeline = [
                model1.ACTION_UPVOTE_POST,
                model1.ACTION_FOLLOW_TOPIC
                ]
        # TODO Will be updated when supporting adding
        # post/topic/comments. See ruuxee.model.v1.ALL_TIMELINE_ACTIONS

        self.source_target_in_timeline = {
                model1.ACTION_UPVOTE_POST: [\
                        self.to_person_id, self.from_post_id],
                model1.ACTION_FOLLOW_TOPIC: [\
                        self.to_person_id, self.to_topic_id],
                }

        self.actions_out_of_timeline = [
                model1.ACTION_DOWNVOTE_POST,
                model1.ACTION_NEUTRALIZE_POST,
                model1.ACTION_UNFOLLOW_TOPIC,
                model1.ACTION_FOLLOW_PERSON
                ]

        self.source_target_out_of_timeline = {
                model1.ACTION_DOWNVOTE_POST: [\
                        self.to_person_id, self.from_post_id],
                model1.ACTION_NEUTRALIZE_POST: [\
                        self.to_person_id, self.from_post_id],
                model1.ACTION_UNFOLLOW_TOPIC: [\
                        self.to_person_id, self.to_topic_id],
                model1.ACTION_FOLLOW_PERSON: [\
                        self.to_person_id, self.from_person_id],
                }


    def tearDown(self):
        self.queue.push_queue(model1.MESSAGE_QUEUE_STOP_SIGN)
        self.processor.join()
        BaseEnvironment.setUp(self)

    def helper_pre_test(self):
        self.helper_empty_queue()
        with self.app.test_client() as c:
            # Setup enviroment.
            # 1. From_person must follow to_person.
            # 2. To_person must neutralize from_post
            path = '/apis/web/v1/follow/person'
            self.helper_post('%s/%s' % (path, self.to_person_id))
            self.assertEqual(self.helper_wait_queue_empty(2), True)
            # Clear this notification or it will affect tasks by
            # dropping an item in notification list.
            pid = self.to_person_id
            table_name = model1.TableNameGenerator.person_notification(pid)
            self.cache.initialize_list(table_name)

            pid = self.from_post_id
            table_name = model1.TableNameGenerator.post_upvote(pid)
            self.helper_post_message(model1.ACTION_NEUTRALIZE_POST,
                                     self.to_person_id,
                                     self.from_post_id,
                                     "")
            self.assertEqual(self.helper_wait_queue_empty(2), True)

    def helper_post_test(self):
        # Environment clearnup
            # 1. From_person must unfollow to_person.
            # 2. To_person must neutralize from_post
        path = '/apis/web/v1/unfollow/person'
        self.helper_post('%s/%s' % (path, self.to_person_id))
        self.assertEqual(self.helper_wait_queue_empty(2), True)
        pid = self.from_post_id

        table_name = model1.TableNameGenerator.post_upvote(pid)
        self.helper_post_message(model1.ACTION_NEUTRALIZE_POST,
                                 self.to_person_id,
                                 self.from_post_id,
                                 "")
        self.assertEqual(self.helper_wait_queue_empty(2), True)

        pid = self.from_person_id
        table_name = model1.TableNameGenerator.person_notification(pid)
        self.cache.initialize_list(table_name)
        pid = self.from_person_id
        table_name = model1.TableNameGenerator.person_timeline(pid)
        self.cache.initialize_list(table_name)

    def test_notifications(self):
        """Case 1: Notification is sent to target person's notification
        list.
        1.1 When target person is followed.
        1.2 When a post of target person is upvoted.
        
        Case 2: Repeated behavior will NOT trigger notification.
        Case 3: Some actions will not trigger notifications.
        2.1 When downvote or neutralize a post.
        2.2 When follow or unfollow a topic.
        2.3 When unfollow a person.
        """

        actions_no_notifications = [
                model1.ACTION_DOWNVOTE_POST,
                model1.ACTION_NEUTRALIZE_POST,
                model1.ACTION_UNFOLLOW_PERSON,
                model1.ACTION_FOLLOW_TOPIC,
                model1.ACTION_UNFOLLOW_TOPIC
                ]

        path_no_notifications = {
                model1.ACTION_DOWNVOTE_POST: '/apis/web/v1/downvote/post',
                model1.ACTION_NEUTRALIZE_POST: '/apis/web/v1/neutralize/post',
                model1.ACTION_UNFOLLOW_PERSON: '/apis/web/v1/unfollow/person',
                model1.ACTION_FOLLOW_TOPIC: '/apis/web/v1/follow/topic',
                model1.ACTION_UNFOLLOW_TOPIC: '/apis/web/v1/unfollow/topic'
                }

        target_no_notifications = {
                model1.ACTION_DOWNVOTE_POST: self.to_post_id,
                model1.ACTION_NEUTRALIZE_POST: self.to_post_id,
                model1.ACTION_UNFOLLOW_PERSON: self.to_person_id,
                model1.ACTION_FOLLOW_TOPIC: self.to_topic_id,
                model1.ACTION_UNFOLLOW_TOPIC: self.to_topic_id,
                }

        actions_in_notifications = [
                model1.ACTION_UPVOTE_POST,
                model1.ACTION_FOLLOW_PERSON
                ]

        path_in_notifications = {
                model1.ACTION_UPVOTE_POST: '/apis/web/v1/upvote/post',
                model1.ACTION_FOLLOW_PERSON: '/apis/web/v1/follow/person'
                }

        target_in_notifications = {
                model1.ACTION_UPVOTE_POST: self.to_post_id,
                model1.ACTION_FOLLOW_PERSON: self.to_person_id
                }

        actions_clear_env = [
                model1.ACTION_NEUTRALIZE_POST,
                model1.ACTION_UNFOLLOW_PERSON
                ]

        path_clear_env = {
                model1.ACTION_NEUTRALIZE_POST: '/apis/web/v1/neutralize/post',
                model1.ACTION_UNFOLLOW_PERSON: '/apis/web/v1/unfollow/person'
                }

        target_clear_env = {
                model1.ACTION_NEUTRALIZE_POST: self.to_post_id,
                model1.ACTION_UNFOLLOW_PERSON: self.to_person_id
                }

        self.helper_pre_test()

        # Case 3: Other actions will not trigger notifications.
        with self.app.test_client() as c:
            for each_action in actions_no_notifications:
                path = path_no_notifications[each_action]
                target_id = target_no_notifications[each_action]
                ts = utils.stimestamp()
                resp = self.helper_post('%s/%s' % (path, target_id))
                data = json.loads(resp.data)
                self.assertEqual(self.helper_wait_queue_empty(2), True)
                # We will not be able to see new notifications.
                pid = self.to_person_id
                table = model1.TableNameGenerator.person_notification(pid)
                record = self.cache.get_list_range(table, 0, 10)
                # There are only two notifications, from previous Case 1
                # execution.
                self.assertEqual(len(record), 0)

        # Case 1: Actions that can invoke notification will take effect.
        with self.app.test_client() as c:
            for each_action in actions_in_notifications:
                path = path_in_notifications[each_action]
                target_id = target_in_notifications[each_action]
                ts = utils.stimestamp()
                resp = self.helper_post('%s/%s' % (path, target_id))
                data = json.loads(resp.data)
                self.assertEqual(self.helper_wait_queue_empty(2), True)
                # Now we should be able to see notifications in
                # to_person_id's list.
                pid = self.to_person_id
                table = model1.TableNameGenerator.person_notification(pid)
                record = self.cache.get_list_range(table, 0, 1)
                item = model1.HistoryItem.create_from_record(record[0])
                self.assertEqual(item.action, each_action)
                self.assertEqual(item.source_id, self.from_person_id)
                self.assertEqual(item.target_id, target_id)
                self.assertEqual(item.addition_id, "")
                self.assertEqual(int(item.stimestamp) - ts <= 1, True)

        # Case 2: Repeated action can't invoke notifications, even
        # valid.
        with self.app.test_client() as c:
            for each_action in actions_in_notifications:
                path = path_in_notifications[each_action]
                target_id = target_in_notifications[each_action]
                ts = utils.stimestamp()
                resp = self.helper_post('%s/%s' % (path, target_id))
                data = json.loads(resp.data)
                self.assertEqual(self.helper_wait_queue_empty(3), True)
                # We will not be able to see new notifications.
                pid = self.to_person_id
                table = model1.TableNameGenerator.person_notification(pid)
                record = self.cache.get_list_range(table, 0, 10)
                # There are only two notifications, from previous Case 1
                # execution.
                self.assertEqual(len(record), 2)
        self.helper_post_test()

    def helper_test_timeline_notification_ranges(self, operation,
                                    actions_in, source_target_in,
                                    actions_out, source_target_out):
        self.helper_pre_test()
        with self.app.test_client() as c:
            # Case
            # Verify updates from persons followed by current person can
            # push their updates to current persons' timeline.

            # Case 1-3: items that will be reflected in timeline.
            timeline_previous_items = 0
            for each_action in actions_in:
                # Assume we have two persons: bourne.zhu and fuzhou.chen.
                # Actions performed by fuzhou.chen can be seen from timeline
                # of bourne.zhu.
                source = source_target_in[each_action][0]
                target = source_target_in[each_action][1]
                self.helper_post_message(each_action, source, target, "")
                # Sleep for a while to wait for backend.
                self.assertEqual(self.helper_wait_queue_empty(2), True)
                path = '/apis/web/v1/%s/range/0/100' % operation
                resp = self.helper_get(path)
                data = json.loads(resp.data)
                timeline_items = len(data["data"])
                delta = timeline_items - timeline_previous_items
                self.assertEqual(delta, 1)
                timeline_previous_items = timeline_items
                from_obj = data["data"][0]["from"]
                to_obj = data["data"][0]["to"]
                self.assertEqual(data["data"][0]["action"], each_action)
                self.assertEqual(from_obj["visible_id"], source)
                self.assertEqual(to_obj["visible_id"], target)

            # Caes 4-6: items that will NOT be reflected in timeline.
            for each_action in actions_out:
                # Assume we have two persons: bourne.zhu and fuzhou.chen.
                # Actions performed by fuzhou.chen can be seen from timeline
                # of bourne.zhu.
                source = source_target_out[each_action][0]
                target = source_target_out[each_action][1]
                self.helper_post_message(each_action, source, target, "")
                # Sleep for a while to wait for backend.
                self.assertEqual(self.helper_wait_queue_empty(2), True)
                path = '/apis/web/v1/%s/range/0/100' % operation
                resp = self.helper_get(path)
                data = json.loads(resp.data)
                timeline_items = len(data["data"])
                delta = timeline_items - timeline_previous_items
                self.assertEqual(delta, 0)

            # Case 7-9
            bad_begin_end = [
                    [ "hello", "100", ruuxee.httplib.BAD_REQUEST ],
                    [ "0", "world", ruuxee.httplib.BAD_REQUEST ],
                    [ "-1", "100", ruuxee.httplib.BAD_REQUEST ],
                    [ "0", "-100", ruuxee.httplib.BAD_REQUEST ],
                    [ "1.2", "100", ruuxee.httplib.BAD_REQUEST ],
                    [ "0", "3.7", ruuxee.httplib.BAD_REQUEST ],
                    [ "100", "0", ruuxee.httplib.METHOD_NOT_ALLOWED ]
                    ]
            for each_test_set in bad_begin_end:
                path = "/apis/web/v1/%s/range/%s/%s" % \
                        (operation, each_test_set[0], each_test_set[1])
                resp = self.helper_get(path, each_test_set[2])
        self.helper_post_test()

    def test_notification_ranges(self):
        """Case: Verify notification can receive items below in timeline:
        1. When followed by a person.
        2. When post is updated by a person.

        And the following actions do not cause updates in timeline.
        3. When downvote a post.
        4. When neutralize a post.
        5. When unfollow a person.
        6. When follow a topic.
        7. When unfollow a topic.

        All cases here also verify that the order of returned timeline
        ranges is from latest to oldest.

        Case 8: If passed in data is negative number then it returns
        error.
        Case 9: If begin >= end then it returns error.
        Case 10: If begin or end is not integer then it returns error."""

        self.helper_test_timeline_notification_ranges(
                "notification",
                self.actions_in_notification,
                self.source_target_in_notification,
                self.actions_out_of_notification,
                self.source_target_out_of_notification)

    def test_timeline_ranges(self):
        """Case: Verify timeline can receive items below in timeline:
        1. When follow a new person.
        2. When upvote a post.
        3. When follow a topic.

        And the following actions do not cause updates in timeline.
        4. When downvote a post.
        5. When neutralize a post.
        6. When unfollow a person.

        All cases here also verify that the order of returned timeline
        ranges is from latest to oldest.

        Case 7: If passed in data is negative number then it returns
        error.
        Case 8: If begin >= end then it returns error.
        Case 9: If begin or end is not integer then it returns error."""
        self.helper_test_timeline_notification_ranges(
                "timeline",
                self.actions_in_timeline,
                self.source_target_in_timeline,
                self.actions_out_of_timeline,
                self.source_target_out_of_timeline)

    def helper_timeline_notification_update(self, operation,
                                        actions_in, source_target_in):
        """Test timeline and notification updates.
        1: A timestamp newer than now returns BAD_REQUEST
        2: Invalid timestamp value returns BAD_REQUEST
        3: Valid timestamp returns correct items.
        """
        self.helper_pre_test()
        # Test 1: Timestamp newer than now returns BAD_REQUEST.
        # Test 2: An invalid timestamp also causes BAD_REQUEST.
        with self.app.test_client() as c:
            now = utils.stimestamp()
            bad_ts = now + 1000
            path = "/apis/web/v1/%s/update/%d" % (operation, bad_ts)
            resp = self.helper_get(path, ruuxee.httplib.BAD_REQUEST)

            path = "/apis/web/v1/%s/update/invalid" % operation
            resp = self.helper_get(path, ruuxee.httplib.BAD_REQUEST)

        # Test 3: Valid timestamp return correct results
        update_count = 1
        with self.app.test_client() as c:
            for each_action in actions_in:
                # Step 1: Prepare environment
                source = source_target_in[each_action][0]
                target = source_target_in[each_action][1]
                self.helper_post_message(each_action, source, target, "")
                # Sleep for a while to wait for backend.
                self.assertEqual(self.helper_wait_queue_empty(2), True)

                # Step 2: Suppose one item is listed in history.
                path = "/apis/web/v1/%s/range/0/100" % operation
                resp = self.helper_get(path)
                data = json.loads(resp.data)
                self.assertEqual(len(data["data"]), update_count)
                ts = int(data["data"][0]["timestamp"])

                # Step 3: Get items with valid timestamp
                valid_ts = ts - 100
                path = "/apis/web/v1/%s/update/%d" % (operation, valid_ts)
                resp = self.helper_get(path)
                resp = self.helper_get(path)
                data = json.loads(resp.data)
                self.assertEqual(len(data["data"]), update_count)

                update_count += 1
        self.helper_post_test()

    def test_timeline_update(self):
        self.helper_timeline_notification_update("timeline",
                                        self.actions_in_timeline,
                                        self.source_target_in_timeline)

    def test_notification_update(self):
        self.helper_timeline_notification_update("notification",
                                        self.actions_in_notification,
                                        self.source_target_in_notification)
