#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"""A set of mock object to represent object model."""

import ruuxee.models.v1 as model1
import time
import string
import random
import hashlib

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

    def persons(self):
        return self.__persons
    def posts(self):
        return self.__posts
    def topics(self):
        return self.__topics

    def __init__(self):
        self.__persons = []
        self.__posts = []
        self.__topics = []
        # Create random data
        for each_person in Database.person_names:
            p = Person()
            rand = self.__get_random_visible_id_str()
            p.visible_id = int(rand)
            p.anonymous_sha1 = hashlib.sha1(rand).hexdigest()
            p.status = random.choice(model1.ALL_PERSON_STATUS)
            p.name = each_person["name"]
            p.readable_id = each_person["readable_id"]
            p.email = each_person["readable_id"] + "@ruuxee.com"
            p.password = rand + p.readable_id
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
        for i in range(100, random.randint(100, 200)):
            po = Post()
            rand = self.__get_random_visible_id_str()
            po.visible_id = int(rand)
            po.status = random.choice(model1.ALL_POST_STATUS)
            po.is_anonymous = random.choice([True, False])
            author = random.choice(self.__persons)
            po.author_visible_id = author.visible_id
            po.written_timestamp = \
                    time.time() + random.randint(100000, 500000)
            po.title = random.choice(Database.post_titles) % \
                                    random.choice(Database.person_names)
            po.content_html = \
                    u"很久很久以前，有一个%s的故事..." % author.city
            self.__posts.append(po)

        for each_title in Database.topic_titles:
            to = Topic()
            rand = self.__get_random_visible_id_str()
            to.visible_id = int(rand)
            to.title = each_title
            to.description = random.choice(["如题", ""])
            self.__topics.append(to)
        # all done.

class Redis(object):
    "A fake Redis database object."
    pass

class Person(object):
    "A mock object for querying person information."
    pass

class Post(object):
    "A mock object for querying posts."
    pass

class Topic(object):
    "A mock object for querying topics."
    pass
