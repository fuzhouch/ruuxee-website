#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

PERSON_STATUS_REGISTERED = 1
PERSON_STATUS_REVIEWING = 2
PERSON_STATUS_DELETED = 3

POST_STATUS_POSTED = 1
POST_STATUS_REVIWING = 2
POST_STATUS_DELETED = 3

PERSON_ACTION_LOGIN = 'a'
PERSON_ACTION_LOGOUT = 'b'
PERSON_ACTION_FOLLOW_PERSON = 'c'
PERSON_ACTION_UNFOLLOW_PERSON = 'd'
PERSON_ACTION_FOLLOW_TOPIC = 'e'
PERSON_ACTION_UNFOLLOW_TOPIC = 'f'
PERSON_ACTION_UPVOTE_POST = 'g'
PERSON_ACTION_UNUPVOTE_POST = 'h'
PERSON_ACTION_DOWNVOTE_POST = 'i'
PERSON_ACTION_UNDOWNVOTE_POST = 'j'
PERSON_ACTION_APPRECIATE_POST = 'k'
PERSON_ACTION_ADD_POST = 'l'
PERSON_ACTION_EDIT_POST = 'm'
PERSON_ACTION_DELETE_POST = 'n'
PERSON_ACTION_ADD_COMMENT = 'o'
PERSON_ACTION_EDIT_COMMENT = 'p'
PERSON_ACTION_REMOVE_COMMENT = 'q'

ALL_PERSON_STATUS = [
        PERSON_STATUS_REVIEWING,
        PERSON_STATUS_REVIEWING,
        PERSON_STATUS_DELETED ]

ALL_POST_STATUS = [
        POST_STATUS_POSTED,
        POST_STATUS_REVIWING,
        POST_STATUS_DELETED ]

ALL_PERSON_STATUS = [
        PERSON_ACTION_LOGIN,
        PERSON_ACTION_LOGOUT,
        PERSON_ACTION_FOLLOW_PERSON,
        PERSON_ACTION_UNFOLLOW_PERSON,
        PERSON_ACTION_FOLLOW_TOPIC,
        PERSON_ACTION_UNFOLLOW_TOPIC,
        PERSON_ACTION_UPVOTE_POST,
        PERSON_ACTION_UNUPVOTE_POST,
        PERSON_ACTION_DOWNVOTE_POST,
        PERSON_ACTION_UNDOWNVOTE_POST,
        PERSON_ACTION_APPRECIATE_POST,
        PERSON_ACTION_ADD_POST,
        PERSON_ACTION_EDIT_POST,
        PERSON_ACTION_DELETE_POST,
        PERSON_ACTION_ADD_COMMENT,
        PERSON_ACTION_EDIT_COMMENT,
        PERSON_ACTION_REMOVE_COMMENT ]

import flask
class DataAccess(object):
    def __init__(self, database, cache):
        self.__db = database
        self.__cache = cache
        pass
    def get_person_brief(self, person_id):
        # Brief information contains only the following fields. They are
        # supposed to be used in hovering popup window.
        fields = ["name", "visible_id", "readable_id", "company"]
        data = None
        try:
            check_id = int(person_id)
            data = self.__db.query_person('visible_id', check_id, fields)
        except Exception: # Invalid visible ID, try user ID again.
            data = self.__db.query_person('readable_id', person_id, fields)
        return data

    @property
    def db(self):
        return self.__db
