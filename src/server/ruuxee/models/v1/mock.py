#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by r.co, All rights reserved.
"""A set of mock object to represent object model."""

import ruuxee.models.v1 as model1
import time
import string
import random
import hashlib
import threading

class Person(object):
    pass

class Post(object):
    pass

class Topic(object):
    pass

class Database(object):
    cities = [ u"腾冲", u"嘉兴", u"雪乡", u"乌兰察布", u"通县", u"长湖镇" ]
    countries = [ u"天朝", u"Middle Earth", u"爱沙尼亚" ]
    person_jobs = [ u"影迷", u"后期", u"编剧", u"程序员", u"设计师" ]
    post_titles = [ u'我看见%s去会娴雅叙！',
                    u'东方红，太阳升，中国出了一个%s',
                    u'讲农业，学大寨；看如戏，跟%s' ]
    topic_titles = [ u'如戏的八卦有哪些？',
                     u'为什么博文总是能打出让人囧囧有神的用词？',
                     u'怎么起一个让人热血沸腾的口号？']
    person_names = [
            {
                "readable_id": u"bourne.zhu",
                "status": model1.STATUS_ACTIVATED,
                "name": u"朱博文"
            },
            {
                "readable_id": u"bindy.xie",
                "name": u"谢彬欢"
            },
            {
                "readable_id": u"wenyu.zhou",
                "name": u"周文宇"
            },
            {
                "readable_id": u"ning.wang",
                "name": u"王宁"
            },
            {
                "readable_id": u"xiayu",
                "name": u"夏宇"
            },
            {
                "readable_id": u"fuzhou.chen",
                "status": model1.STATUS_ACTIVATED,
                "name": u"陈甫鸼"
            },
            {
                "readable_id": u"weixuan.lu",
                "name": u"阿虚"
            },
            {
                "readable_id": u"xiuen.jin",
                "name": u"金秀恩"
            },
            {
                "readable_id": u"rong.yu",
                "name": u"于容"
            }
        ]

    def __get_random_visible_id_str(self):
        return u"".join(random.choice(string.digits) for i in range(8))

    @property
    def persons(self):
        return self.__persons

    @property
    def posts(self):
        return self.__posts

    @property
    def topics(self):
        return self.__topics

    def query_person(self, key, value, fields):
        return self.__query_object(self.__persons, key, value, fields)
    def query_post(self, key, value, fields):
        return self.__query_object(self.__posts, key, value, fields)
    def query_topic(self, key, value, fields):
        return self.__query_object(self.__topics, key, value, fields)

    def __query_object(self, table, key, value, fields):
        found_objects = []
        for each_object in table:
            object_dict = each_object.__dict__
            # Note: Comparison is case sensitive
            if key in object_dict and object_dict[key] == value:
                found = {}
                for each_field in fields:
                    if each_field in object_dict:
                        found[each_field] = object_dict[each_field]
                found_objects.append(found)
        if len(found_objects) > 0:
            return found_objects
        return None

    def __init__(self, cache):
        self.__persons = []
        self.__posts = []
        self.__topics = []
        # Create random data
        for each_person in Database.person_names:
            p = Person()
            p.visible_id = self.__get_random_visible_id_str()
            p.anonymous_sha1 = hashlib.sha1(p.visible_id).hexdigest()
            if "status" in each_person:
                p.status = each_person["status"]
            else:
                p.status = random.choice(model1.ALL_PERSON_STATUS)
            p.name = each_person["name"]
            p.readable_id = each_person["readable_id"]
            p.email = each_person["readable_id"] + "@r.co"
            p.password = p.readable_id
            p.password_sha1 = hashlib.sha1(p.password).hexdigest()
            p.signup_timestamp = \
                    time.time() + random.randint(100000, 500000)
            p.avartar_url = ""
            p.description = random.choice([u"Good person", u'懒虫', u""])
            p.job = random.choice(Database.person_jobs)
            p.company = u"如戏"
            p.city = random.choice(Database.cities)
            p.country = random.choice(Database.countries)
            self.__persons.append(p)
        for i in range(100, random.randint(120, 200)):
            po = Post()
            po.visible_id = self.__get_random_visible_id_str()
            po.status = random.choice(model1.ALL_POST_STATUS)
            po.is_anonymous = random.choice([True, False])
            author = random.choice(self.__persons)
            po.author_visible_id = author.visible_id
            po.written_timestamp = \
                    time.time() + random.randint(100000, 500000)
            name = random.choice(Database.person_names)["name"]
            po.title = random.choice(Database.post_titles) % name
                            
            po.content_html = \
                    u"很久很久以前，有一个%s的故事，主角是%s" % \
                    (author.city, author.name)
            po.brief_text = u"有一个%s的故事..." % author.city
            self.__posts.append(po)

        for each_title in Database.topic_titles:
            to = Topic()
            to.visible_id = self.__get_random_visible_id_str()
            to.title = each_title
            to.description = random.choice([u"如题", u"No much to talk"])
            self.__topics.append(to)
        # all done for fake database. Now create cache for persons.
        for each_person in self.__persons:
            model1.initialize_person_cache(cache, each_person.visible_id)
        for each_post in self.__posts:
            model1.initialize_post_cache(cache, each_post.visible_id)
        for each_topic in self.__topics:
            model1.initialize_topic_cache(cache, each_topic.visible_id)

        # Let's always set author of first post as bourne.zhu for test
        # purposes.
        target_id = self.__persons[0].visible_id
        self.__posts[0].author_visible_id = target_id

class MessageQueue(object):
    """
    A fake message queue. It is designed to support two scenarios:
    Unit test (single threaded) or functional test with fake data
    (multiple threaded).
    same
    """
    def __init__(self, with_worker=False):
        self.__queue = []
        self.__with_worker = with_worker
        self.__ready = None
        self.set_with_worker(with_worker)

    def set_with_worker(self, status = False):
        self.__with_worker = status
        if self.__with_worker:
            self.__ready = threading.Condition()

    @property
    def queue(self):
        return self.__queue

    def push_queue(self, record):
        if self.__with_worker:
            with self.__ready:
                self.__queue.insert(0, record)
                self.__ready.notify()
        else:
            self.__queue.insert(0, record)

    def pop_queue(self):
        # NOTE
        # We do not check if set already exist and THIS IS AS EXPECTED.
        # We expect all necessary tables are created when an entity was
        # created. If there's any steps that does not do this job, it
        # should crash here when running unit test with mock.
        #
        # In real environment the real Redis message queue should block
        # here.
        if self.__with_worker:
            with self.__ready:
                if len(self.__queue) == 0:
                    self.__ready.wait()
                return self.__queue.pop()
        else:
            return self.__queue.pop()

class Cache(object):
    def __init__(self):
        self.__lists = {}
        self.__tables = {}
        self.__sets = {}

    @property
    def sets(self):
        return self.__sets

    @property
    def tables(self):
        return self._tables

    @property
    def lists(self):
        return self.__lists

    def initialize_set(self, set_name):
        self.__sets[set_name] = set()

    def insert_set(self, set_name, value):
        # NOTE
        # We do not check if set already exist and THIS IS AS EXPECTED.
        # We expect all necessary tables are created when an entity was
        # created. If there's any steps that does not do this job, it
        # should crash here when running unit test with mock.
        self.__sets[set_name].add(value)

    def remove_set(self, set_name, value):
        # NOTE
        # We do not check if set already exist and THIS IS AS EXPECTED.
        # We expect all necessary tables are created when an entity was
        # created. If there's any steps that does not do this job, it
        # should crash here when running unit test with mock.
        self.__sets[set_name].remove(value)

    def get_full_set(self, set_name):
        return self.__sets[set_name]

    def initialize_list(self, list_name):
        self.__lists[list_name] = []

    def in_set(self, set_name, value):
        return value in self.__sets[set_name]

    def append_list(self, list_name, value):
        self.__lists[list_name].append(value)

    def prepend_list(self, list_name, value):
        self.__lists[list_name].insert(0, value)

    def remove_list(self, list_name, value):
        self.__lists[list_name].remove(value)

    def in_list(self, list_name, value):
        return value in self.__lists[list_name]

    def get_list_range(self, list_name, begin, end):
        return self.__lists[list_name][begin:end]

    def get_list_length(self, list_name):
        return len(self.__lists[list_name])

class AlwaysBourneZhuWebSession(object):
    """A fake WebSession that deal with login session.

    The fake web session always consider user as bourne.zhu. So web UI
    developers can test single page, without the needs of really doing
    any logon session. This is very useful when running unittest.
    """
    def __init__(self, database):
        self.__db = database
        pass
    def validate(self, request):
        # No matter what happen, always predict authentication success.
        # This is important for web UI developers to test UI without
        # authentication.
        return True

    def authenticated_person_visible_id(self):
        return self.__db.persons[0].visible_id

    def authenticated_person_readable_id(self):
        return self.__db.persons[0].readable_id

    def authenticated_person_name(self):
        return self.__db.persons[0].name

class NoPasswordCheckSession(object):
    """A fake web session allow people authentication, with default
    value if you don't do so.
    
    The login session can be changed when user go through login process.
    Or, if the first page does not do this, return default bourne.zhu."""
    def __init__(self, database):
        self.__db = database
        self.__authenticated_person_visible_id = None
        self.__authenticated_person_readable_id = None
        self.__authenticated_person_name = None
        pass

    def validate(self, request):
        # In real production we may choose to use Email as login name
        login_name = request.form["username"]
        # A fake session manager never check password. Just to change
        # user.
        fields = [ "visible_id", "readable_id", "name" ]
        data = self.__db.query_person("readable_id", login_name, fields)
        if data is None:
            return False
        assert len(data) == 1
        self.__authenticated_person_visible_id = data[0]["visible_id"]
        self.__authenticated_person_readable_id = data[0]["readable_id"]
        self.__authenticated_person_name = data[0]["name"]
        return True

    def logout(self):
        self.__authenticated_person_visible_id = None
        self.__authenticated_person_readable_id = None
        self.__authenticated_person_name = None

    def authenticated_person_visible_id(self):
        if self.__authenticated_person_visible_id is None:
            return self.__db.persons[0].visible_id
        return self.__authenticated_person_visible_id

    def authenticated_person_readable_id(self):
        if self.__authenticated_person_readable_id is None:
            return self.__db.persons[0].readable_id
        return self.__authenticated_person_readable_id

    def authenticated_person_name(self):
        if self.__authenticated_person_name is None:
            return self.__db.persons[0].name
        return self.__authenticated_person_name


class AlwaysFalseWebSession(object):
    """A fake WebSession that always return login failure.

    This is a useful mock to test page redirection and API failure.
    """
    def __init__(self, database):
        pass
    def validate(self, request):
        return False

    def authenticated_user_visible_id(self):
        # No use. And will trigger error if anyone really calls it.
        return None
