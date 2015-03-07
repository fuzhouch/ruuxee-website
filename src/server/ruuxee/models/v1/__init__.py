#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

import ruuxee
import ruuxee.utils as utils
import logging
import re

STATUS_REVIEWING  = 1
STATUS_ACTIVATED  = 2
STATUS_SUSPENDED  = 3
STATUS_REVOKED    = 4
STATUS_DELETED    = 5

ACTION_CREATE_ACCOUNT = 'a'
ACTION_DELETE_ACCOUNT = 'b'
ACTION_UPDATE_ACCOUNT_INFO = 'c'
ACTION_LOGIN = 'd'
ACTION_LOGOUT = 'e'
ACTION_FOLLOW_PERSON = 'f'
ACTION_UNFOLLOW_PERSON = 'g'
ACTION_FOLLOW_TOPIC = 'h'
ACTION_UNFOLLOW_TOPIC = 'i'
ACTION_UPVOTE_POST = 'j'
ACTION_NEUTRALIZE_POST = 'k'
ACTION_DOWNVOTE_POST = 'l'
ACTION_ADD_POST = 'm'
ACTION_EDIT_POST = 'n'
ACTION_DELETE_POST = 'o'
ACTION_ADD_COMMENT = 'p'
ACTION_EDIT_COMMENT = 'q'
ACTION_REMOVE_COMMENT = 'r'
ACTION_ADD_TOPIC = 's'
ACTION_EDIT_TOPIC = 't'
ACTION_REMOVE_TOPIC = 'u'

ALL_PERSON_STATUS = [
        STATUS_REVIEWING,
        STATUS_ACTIVATED,
        STATUS_SUSPENDED,
        STATUS_REVOKED,
        STATUS_DELETED ]

PENDING_STATUS = [
        STATUS_REVIEWING,
        STATUS_SUSPENDED,
        STATUS_REVOKED ]

ALL_POST_STATUS = [
        STATUS_REVIEWING,
        STATUS_ACTIVATED,
        STATUS_SUSPENDED,
        STATUS_DELETED ]

ALL_TOPIC_STATUS = [
        STATUS_REVIEWING,
        STATUS_ACTIVATED,
        STATUS_SUSPENDED,
        STATUS_DELETED ]

TABLE_NAME_PERSON_ACTIONS            = "pa"
TABLE_NAME_PERSON_FOLLOW_PERSON      = "pfp"
TABLE_NAME_PERSON_FOLLOWED_BY_PERSON = "pfbp"
TABLE_NAME_PERSON_TIMELINE           = "pt"
TABLE_NAME_PERSON_FOLLOW_TOPIC       = "pft"
TABLE_NAME_TOPIC_FOLLOWED_BY_PERSON  = "tfbp"
TABLE_NAME_POST_UPVOTE               = "pu"
TABLE_NAME_POST_DOWNVOTE             = "pd"

# The stop sign is used to tell QueueWorker that it should stop.
MESSAGE_QUEUE_STOP_SIGN = '{EOQ}'

ANONYMOUS_PERSON_NAME = u"匿名用户"
REVIEWING_TITLE = u"审核中"
REVIEWING_TEXT = u"该文章正在被审核..."
SUSPENDED_TITLE = u"违反管理条例"
SUSPENDED_TEXT = u"该文章因违反管理条例被要求去除..."

class TableNameGenerator(object):
    @staticmethod
    def person_action(visible_id):
        return "%s%s" % (TABLE_NAME_PERSON_ACTIONS, str(visible_id))

    @staticmethod
    def person_timeline(visible_id):
        return "%s%s" % (TABLE_NAME_PERSON_TIMELINE, str(visible_id))

    @staticmethod
    def person_follow_topic(visible_id):
        return "%s%s" % (TABLE_NAME_PERSON_FOLLOW_TOPIC, str(visible_id))

    @staticmethod
    def topic_followed_by_person(visible_id):
        return "%s%s" % (TABLE_NAME_TOPIC_FOLLOWED_BY_PERSON, str(visible_id))

    @staticmethod
    def person_follow_person(visible_id):
        return "%s%s" % (TABLE_NAME_PERSON_FOLLOW_PERSON, str(visible_id))

    @staticmethod
    def person_followed_by_person(visible_id):
        return "%s%s" % (TABLE_NAME_PERSON_FOLLOWED_BY_PERSON, str(visible_id))

    @staticmethod
    def post_upvote(visible_id):
        return "%s%s" % (TABLE_NAME_POST_UPVOTE, str(visible_id))

    @staticmethod
    def post_downvote(visible_id):
        return "%s%s" % (TABLE_NAME_POST_DOWNVOTE, str(visible_id))

    @staticmethod
    def person_timeline(visible_id):
        return "%s%s" % (TABLE_NAME_PERSON_TIMELINE, str(visible_id))

@utils.Logging.enter_leave
def initialize_person_cache(cache, visible_id):
    """def initialize_person_cache(cache, visible_id)
    Create cache for a specified user. Used when creating a new user
    account."""
    logging.info("initialize_person_cache: %s" % visible_id)
    action_history = TableNameGenerator.person_action(visible_id)
    timeline = TableNameGenerator.person_timeline(visible_id)
    followers = TableNameGenerator.person_follow_person(visible_id)
    followed_by = TableNameGenerator.person_followed_by_person(visible_id)
    topics = TableNameGenerator.person_follow_topic(visible_id)
    cache.initialize_list(action_history)
    cache.initialize_list(timeline)
    cache.initialize_set(followers)
    cache.initialize_set(followed_by)
    cache.initialize_set(topics)

@utils.Logging.enter_leave
def initialize_post_cache(cache, visible_id):
    """def initialize_post_cache(cache, visible_id)
    Create cache for an article when it's created."""
    logging.info("initialize_post_cache: %s" % visible_id)
    upvotes = TableNameGenerator.post_upvote(visible_id)
    downvotes = TableNameGenerator.post_downvote(visible_id)
    cache.initialize_list(upvotes)
    cache.initialize_list(downvotes)

@utils.Logging.enter_leave
def initialize_topic_cache(cache, visible_id):
    """def initialize_post_cache(cache, visible_id)
    Create cache tables for a topic when it's created."""
    logging.info("initialize_post_topic: %s" % visible_id)
    followers = TableNameGenerator.topic_followed_by_person(visible_id)
    cache.initialize_set(followers)

class HistoryItem(object):
    "An internal helper object to decode and encode item in timeline."
    def __init__(self, stimestamp, action, source, target, addition):
        self.__stimestamp = stimestamp
        self.__action = action
        self.__source = source
        self.__target = target
        self.__addition = addition

    @staticmethod
    def create_from_record(record):
        item = HistoryItem("", "", "", "", "")
        item.decode(record)
        return item

    def decode(self, record):
        data = record.split(":")
        sections = len(data)
        if sections == 5:
            self.__stimestamp = data[0]
            self.__action = data[1]
            self.__source = data[2]
            self.__target = data[3]
            self.__addition = data[4]
        elif sections == 3:
            self.__stimestamp = data[0]
            self.__action = data[1]
            self.__target = data[2]
        else:
            raise ValueError("Bad data: %s" % record)

    def encode(self):
        record = "%d:%s:%s:%s:%s" % (self.__stimestamp,\
                                     self.__action,
                                     self.__source,
                                     self.__target,
                                     self.__addition)
        return record

    def encode_short(self):
        """def encode_short(self) -> string record

        Encode data in short form. Used with notification items.
        """
        record = "%d:%s:%s:" % (self.__stimestamp,\
                                self.__action,
                                self.__target)
        return record

    @property
    def stimestamp(self):
        return self.__stimestamp

    @property
    def action(self):
        return self.__action

    @property
    def source_id(self):
        return self.__source

    @property
    def target_id(self):
        return self.__target

    @property
    def addition_id(self):
        return self.__addition

class Core(utils.Logging):
    "The main module to provide Apis for web handler."
    def __init__(self, database, cache, queue):
        self.__db = database
        self.__cache = cache
        self.__queue = queue
        utils.Logging.__init__(self)

    @property
    def db(self):
        return self.__db

    @property
    def cache(self):
        return self.__cache

    @property
    def queue(self):
        return self.__queue

    def is_actionable_post(self, post_visible_id):
        """def is_actionable_post(self, post_visible_id) -> HTTP code

        Check if a post can be followed or voted. A post
        under reviewing, or suspended, or revoked, or deleted,
        cannot take action.

        This function returns different HTTP codes on different account
        types:
            BAD_REQUEST for invalid user ID
            METHOD_NOT_ALLOWED for non-activated ID
            OK for success"""
        return self.__is_actionable(post_visible_id, self.__db.query_post)

    def is_actionable_person(self, person_visible_id):
        """def is_actionable_person(self, person_visible_id) -> HTTP code

        Check if a person can do any action in this web site. A
        user under reviewing, or suspended, or revoked, or deleted,
        cannot take action.

        This function returns different HTTP codes on different account
        types:
            BAD_REQUEST for invalid user ID
            METHOD_NOT_ALLOWED for non-activated ID
            OK for success"""
        return self.__is_actionable(person_visible_id,\
                                    self.__db.query_person)

    def is_actionable_topic(self, topic_visible_id):
        """def is_actionable_post(self, topic_visible_id) -> HTTP code

        Check if a topic can accept changes. A topic can be suspended or
        deleted, which cannot take any actions.

        This function returns different HTTP codes on different account
        types:
            BAD_REQUEST for invalid user ID
            METHOD_NOT_ALLOWED for non-activated ID
            OK for success"""
        return self.__is_actionable(topic_visible_id, self.__db.query_topic)

    @utils.Logging.enter_leave
    def get_person_brief(self, person_id):
        # TODO
        # Brief information contains only the following fields. They are
        # supposed to be used in hovering popup window.
        fields = ["name", "visible_id", "readable_id", "company"]
        data = self.__db.query_person("visible_id", person_id, fields)
        if data is None:
            data = self.__db.query_person("readable_id", person_id, fields)

        if data is not None:
            return data[0]
        else:
            return None

    @utils.Logging.enter_leave
    def get_topic_brief(self, topic_id):
        # TODO
        # Brief information contains only the following fields. They are
        # supposed to be used in hovering popup window.
        fields = [ "visible_id", "title", "description"]
        data = self.__db.query_topic("visible_id", topic_id, fields)

        if data is not None:
            return data[0]
        else:
            return None

    @utils.Logging.enter_leave
    def get_post_brief(self, post_visible_id):
        return self.__get_post(post_visible_id, full=False)

    @utils.Logging.enter_leave
    def get_post(self, post_visible_id):
        return self.__get_post(post_visible_id, full=True)

    @utils.Logging.enter_leave
    def follow_person(self, current_person_id, follow_person_id):
        """def follow_person(self, current_person_id, follow_person_id)

        Make one person follow another person. Both persons must be
        actionable."""
        current = str(current_person_id)
        target = str(follow_person_id)
        if current == target:
            return self.__response(ruuxee.httplib.METHOD_NOT_ALLOWED)

        status = self.is_actionable_person(current)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.is_actionable_person(target)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        # NOTE
        # It is very difficult to reject a temptation here, that we may
        # want to introduce a potential "optimization" to avoid
        # duplicated status updating, by checking whether
        # the follow/unfollow relationship is already there (see below): 
        #
        # table_name = TableNameGenerator.person_follow_person(current)
        # if self.__cache.in_set(table_name, target):
        #    # Already followed, do nothing.
        #    return self.__response()
        #
        # However, this can be a bad idea when we have multiple clients
        # sending commands. Think about scenario below:
        #
        #     0. Initial status is Follow.
        #     1. A mobile app sends an Unfollow command and is pushed
        #        into Worker queue.
        #     2. A web app sends a Follow command and start checking
        #        status in Core.
        #     4. Core finds the current status is still Follow, so it
        #        cancels the Follow command from #2. So after the final
        #        status the final status becomes Unfollow.
        #
        # The step above is not correct because it silently ignore the
        # later command. And there is no way to avoid this, unless we add
        # a big lock on check+push commands in both Core and Worker,
        # which may cause performance issue.
        #
        # So the correct way is to let both in queue and get processed.
        #
        # There is another concern here, that bad guys may want to use
        # this to attack of queue, by repeatly sending
        # Follow/Unfollow/Follow commands. I admit it is possible, but I
        # will leave this to Nginx by limiting the RPS (requests per
        # second) from same IP.
        #
        self.log_info("Effective: follow %s %s" % (current, target))

        action = ACTION_FOLLOW_PERSON
        addition = ""
        return self.__post_message(action, current, target, addition)

    @utils.Logging.enter_leave
    def unfollow_person(self, current_person_id, unfollow_person_id):
        """def unfollow_person(self, current_person_id, follow_person_id)

        Make one person follow another person. Both persons must be
        actionable."""
        current = str(current_person_id)
        target = str(unfollow_person_id)
        if current == target:
            return self.__response(ruuxee.httplib.METHOD_NOT_ALLOWED)

        status = self.is_actionable_person(current)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.is_actionable_person(target)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        self.log_info("Effective: unfollow %s %s" % (current, target))

        action = ACTION_UNFOLLOW_PERSON
        addition = ""
        return self.__post_message(action, current, target, addition)

    @utils.Logging.enter_leave
    def follow_topic(self, current_person_id, topic_visible_id):
        """def follow_topic(self, current_person_id, topic_visible_id):

        Make one person follow a topic. The person must be actionable.
        NOTE: The topic may be suspended for administrative reason."""
        current = str(current_person_id)
        target = str(topic_visible_id)

        status = self.is_actionable_person(current)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.is_actionable_topic(target)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        self.log_info("Effective: follow_topic %s %s" % (current, target))

        action = ACTION_FOLLOW_TOPIC
        addition = ""
        return self.__post_message(action, current, target, addition)

    @utils.Logging.enter_leave
    def unfollow_topic(self, current_person_id, topic_visible_id):
        """def unfollow_topic(self, current_person_id, topic_visible_id):

        Make one person unfollow a topic. The person must be actionable.
        NOTE: The topic may be suspended for administrative reason."""
        current = str(current_person_id)
        target = str(topic_visible_id)

        status = self.is_actionable_person(current)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.is_actionable_topic(target)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        self.log_info("Effective: unfollow_topic %s %s" % (current, target))

        action = ACTION_UNFOLLOW_TOPIC
        addition = ""
        return self.__post_message(action, current, target, addition)

    @utils.Logging.enter_leave
    def upvote_post(self, current_person_id, target_post_id):
        """def upvote_post(self, current_person_id, target_post_id)

        Make one person upvote a post. The person and post must be both
        actionable."""
        current = str(current_person_id)
        target = str(target_post_id)

        status = self.is_actionable_person(current)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.is_actionable_post(target)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.__is_post_written_by(target, current)
        if status == ruuxee.httplib.OK:
            return self.__response(ruuxee.httplib.METHOD_NOT_ALLOWED)

        self.log_info("Effective: upvote %s %s" % (current, target))

        action = ACTION_UPVOTE_POST
        addition = ""
        return self.__post_message(action, current, target, addition)

    @utils.Logging.enter_leave
    def downvote_post(self, current_person_id, target_post_id):
        """def downvote_post(self, current_person_id, target_post_id)

        Make one person downvote a post. The person and post must be
        both actionable."""
        current = str(current_person_id)
        target = str(target_post_id)

        status = self.is_actionable_person(current)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.is_actionable_post(target)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.__is_post_written_by(target, current)
        if status == ruuxee.httplib.OK:
            return self.__response(ruuxee.httplib.METHOD_NOT_ALLOWED)

        self.log_info("Effective: upvote %s %s" % (current, target))

        action = ACTION_DOWNVOTE_POST
        addition = ""
        return self.__post_message(action, current, target, addition)

    @utils.Logging.enter_leave
    def neutralize_post(self, current_person_id, target_post_id):
        """def neutralize_post(self, current_person_id, target_post_id)

        Make one person neutralize a post (neither upvote or downvote).
        The person and post must be both actionable."""
        current = str(current_person_id)
        target = str(target_post_id)

        status = self.is_actionable_person(current)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.is_actionable_post(target)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        status = self.__is_post_written_by(target, current)
        if status == ruuxee.httplib.OK:
            return self.__response(ruuxee.httplib.METHOD_NOT_ALLOWED)

        self.log_info("Effective: neutralize %s %s" % (current, target))

        action = ACTION_NEUTRALIZE_POST
        addition = ""
        return self.__post_message(action, current, target, addition)

    @utils.Logging.enter_leave
    def get_timeline_range(self, current_person_id, begin, end):
        """def get_timeline_range(self, current_person_id, begin, end)

        Return specified range of latest updates."""
        current = str(current_person_id)
        try:
            begin_offset = int(begin)
            end_offset = int(end)
        except Exception:
            return self.__response(ruuxee.httplib.BAD_REQUEST)

        if begin_offset < 0 or end_offset < 0:
            return self.__response(ruuxee.httplib.BAD_REQUEST)

        if begin_offset >= end_offset:
            return self.__response(ruuxee.httplib.METHOD_NOT_ALLOWED)

        status = self.is_actionable_person(current)
        if status != ruuxee.httplib.OK:
            return self.__response(status)

        self.log_info("Effective: timeline %s %s %s" % (current, begin, end))
        # It is an synchronized operation, we get it directly from
        # timeline cache.
        table_name = TableNameGenerator.person_timeline(current)
        ret = self.__cache.get_list_range(table_name,\
                                          begin_offset, end_offset)
        response = self.__response(ruuxee.httplib.OK)
        response["data"] = []
        for each_record in ret:
            data = {}
            item = HistoryItem.create_from_record(each_record)
            data["timestamp"] = item.stimestamp
            data["action"] = item.action
            data["from_visible_id"] = item.source_id
            data["to_visible_id"] = item.target_id
            # item.addition is not exposed because it's used for
            # internal reference.
            response["data"].append(data)
        return response

    def __is_post_written_by(self, post_id, person_id):
        fields = ["author_visible_id"]
        try:
            data = self.__db.query_post("visible_id", post_id, fields)
        except Exception: # Invalid visible ID
            return ruuxee.httplib.BAD_REQUEST
        if data is None or len(data) == 0: # ID not found
            return ruuxee.httplib.NOT_FOUND
        author = data[0]["author_visible_id"]
        if author == person_id:
            return ruuxee.httplib.OK
        return ruuxee.httplib.METHOD_NOT_ALLOWED

    def __is_actionable(self, visible_id, query_func):
        fields = ["status"]
        try:
            data = query_func("visible_id", visible_id, fields)
        except Exception: # Invalid visible ID
            return ruuxee.httplib.BAD_REQUEST
        if data is None or len(data) == 0: # ID not found
            return ruuxee.httplib.NOT_FOUND
        status = data[0]["status"]
        if status in PENDING_STATUS: # Suspended user
            return ruuxee.httplib.METHOD_NOT_ALLOWED
        if status == STATUS_DELETED: # Deleted user
            return ruuxee.httplib.NOT_FOUND
        return ruuxee.httplib.OK

    @staticmethod
    def __response(status = ruuxee.httplib.OK):
        return { "status_code" : status }

    def __post_message(self, action, source, target, addition):
        ts = utils.stimestamp()
        item = HistoryItem(ts, action, source, target, addition)
        self.__queue.push_queue(item.encode())
        return self.__response()

    # --------------------------------------------------------------
    # Internal functions below
    # --------------------------------------------------------------

    def __get_author_name(self, data):
        if data["is_anonymous"]:
            author_name = ANONYMOUS_PERSON_NAME
        else:
            author_id = data["author_visible_id"]
            found_person = self.__db.query_person("visible_id", \
                                                  author_id, \
                                                  ["name"])
            # No need to check found_person. It must exist
            # because it is from internal database. The insert
            # logic should have ensured this.                  
            author_name = found_person[0]["name"]
        return author_name

    def __get_post(self, post_visible_id, full = False):
        fields = [ "status", "is_anonymous", "author_visible_id", \
                   "title", "brief_text", "visible_id" ]
        if full:
            fields += [ "written_timestamp", "content_html" ]
        data = None
        result = self.__db.query_post("visible_id", post_visible_id, fields)
        if result is not None:
            single = result[0]
            if single["status"] == STATUS_REVIEWING:
                author_id = single["author_visible_id"]
                author_name = self.__get_author_name(single)
                data = { "status": STATUS_REVIEWING, \
                         "is_anonymous": single["is_anonymous"], \
                         "author_name": author_name, \
                         "title": REVIEWING_TITLE, \
                         "brief_text": REVIEWING_TEXT }
            elif single["status"] == STATUS_SUSPENDED:
                author_id = single["author_visible_id"]
                author_name = self.__get_author_name(single)
                data = { "status": STATUS_SUSPENDED, \
                         "is_anonymous": single["is_anonymous"], \
                         "author_name": author_name, \
                         "title": SUSPENDED_TITLE, \
                         "brief_text": SUSPENDED_TEXT }
            elif single["status"] == STATUS_DELETED:
                data = { "status": STATUS_DELETED }
                return data
            else:
                # Good, a posted article, now adjust other info
                # based on information.
                author_name = self.__get_author_name(single)
                data = { "status": STATUS_ACTIVATED, \
                         "is_anonymous": single["is_anonymous"], \
                         "author_name": author_name, \
                         "title": single["title"], \
                         "brief_text": single["brief_text"] }
            # Important: Make sure we don't return author visible ID for
            # anonymous users.
            if not single["is_anonymous"]:
                data["author_visible_id"] = single["author_visible_id"]
            # Append real content for full mode.
            if full:
                data["written_timestamp"] = single["written_timestamp"]
                data["content_html"] = single["content_html"]
        return data

class RequestWorker(utils.Logging):
    """The worker to process all information in message queue. It is
    running in different process of Core."""
    def __init__(self, database, cache, queue):
        self.__db = database
        self.__cache = cache
        self.__queue = queue
        # pattern of request:
        # {timestamp}:{action}:{from_id}:{to_id}[:{additional_data_id}]
        self.__pattern = re.compile(r"^(\d\d*):(\w\w*):(\d\d*):(\d\d*):(\d*)")
        self.__handlers = {
                ACTION_FOLLOW_PERSON: self.__follow_person,
                ACTION_UNFOLLOW_PERSON: self.__unfollow_person,
                ACTION_FOLLOW_TOPIC: self.__follow_topic,
                ACTION_UNFOLLOW_TOPIC: self.__unfollow_topic,
                ACTION_UPVOTE_POST: self.__upvote_post,
                ACTION_NEUTRALIZE_POST: self.__neutralize_post,
                ACTION_DOWNVOTE_POST: self.__downvote_post
        }
        utils.Logging.__init__(self)

    @property
    def db(self):
        return self.__db

    @property
    def cache(self):
        return self.__cache

    @property
    def queue(self):
        return self.__queue

    @utils.Logging.enter_leave
    def main_loop(self):
        "Start main loop to read message queue."
        while True:
            record = self.__queue.pop_queue()
            if record == MESSAGE_QUEUE_STOP_SIGN:
                self.log_info("STOP_SIGN received. Goodbye.")
                break
            else:
                ts, action, from_id, to_id, addition = \
                                           self.__parse_request(record)
                self.__process_request(ts, action, from_id, to_id, addition)

    @utils.Logging.enter_leave
    def __parse_request(self, record):
        m = self.__pattern.match(record)
        if m is None: # Nothing matched
            self.log_error("bad format: " % record)
            raise ValueError(record)
        else:
            ts = int(m.group(1))
            # NOTE ts must success as it's indeed internal.
            action = m.group(2)
            from_id = m.group(3)
            to_id = m.group(4)
            addition = m.group(5)
        return (ts, action, from_id, to_id, addition)

    @utils.Logging.enter_leave
    def __process_request(self, ts, action, from_id, to_id, addition):
        self.__add_action_history(ts, action, from_id, to_id, addition)
        handler = self.__handlers[action]
        handler(ts, from_id, to_id, addition)

    # ============= Handler functions ==============
    def __follow_person(self, ts, from_id, to_id, addition):
        table_name = TableNameGenerator.person_follow_person(from_id)
        self.__cache.insert_set(table_name, to_id)
        table_name = TableNameGenerator.person_followed_by_person(to_id)
        self.__cache.insert_set(table_name, from_id)
        self.log_info("%s follow %s" % (from_id, to_id))

    def __unfollow_person(self, ts, from_id, to_id, addition):
        table_name = TableNameGenerator.person_follow_person(from_id)
        self.__cache.remove_set(table_name, to_id)
        table_name = TableNameGenerator.person_followed_by_person(to_id)
        self.__cache.remove_set(table_name, from_id)
        self.log_info("%s unfollow %s" % (from_id, to_id))

    def __follow_topic(self, ts, from_id, to_id, addition):
        table_name = TableNameGenerator.person_follow_topic(from_id)
        self.__cache.insert_set(table_name, to_id)
        table_name = TableNameGenerator.topic_followed_by_person(to_id)
        self.__cache.insert_set(table_name, from_id)
        action = ACTION_FOLLOW_TOPIC
        self.__update_follower_timelines(ts, action, from_id, to_id, addition)
        self.log_info("%s follow_topic %s" % (from_id, to_id))

    def __unfollow_topic(self, ts, from_id, to_id, addition):
        table_name = TableNameGenerator.person_follow_topic(from_id)
        self.__cache.remove_set(table_name, to_id)
        table_name = TableNameGenerator.topic_followed_by_person(to_id)
        self.__cache.remove_set(table_name, from_id)
        self.log_info("%s unfollow_topic %s" % (from_id, to_id))

    def __upvote_post(self, ts, from_id, to_id, addition):
        table_name = TableNameGenerator.post_downvote(to_id)
        if self.__cache.in_list(table_name, from_id):
            self.__cache.remove_list(table_name, from_id)
        table_name = TableNameGenerator.post_upvote(to_id)
        self.__cache.prepend_list(table_name, from_id)
        self.log_info("%s upvote %s" % (from_id, to_id))
        action = ACTION_UPVOTE_POST
        self.__update_follower_timelines(ts, action, from_id, to_id, addition)

    def __downvote_post(self, ts, from_id, to_id, addition):
        table_name = TableNameGenerator.post_upvote(to_id)
        if self.__cache.in_list(table_name, from_id):
            self.__cache.remove_list(table_name, from_id)
        table_name = TableNameGenerator.post_downvote(to_id)
        self.__cache.prepend_list(table_name, from_id)
        self.log_info("%s downvote %s" % (from_id, to_id))

    def __neutralize_post(self, ts, from_id, to_id, addition):
        table_name = TableNameGenerator.post_downvote(to_id)
        if self.__cache.in_list(table_name, from_id):
            self.__cache.remove_list(table_name, from_id)
        table_name = TableNameGenerator.post_upvote(to_id)
        if self.__cache.in_list(table_name, from_id):
            self.__cache.remove_list(table_name, from_id)
        self.log_info("%s neutralize %s" % (from_id, to_id))

    def __add_action_history(self, timestamp,\
                             action, current, target, addition):
        table_name = TableNameGenerator.person_action(current)
        data = HistoryItem(timestamp, action, current, target, addition)
        self.__cache.prepend_list(table_name, data.encode())
        self.log_info("table = %s, data = %s" % (table_name, data))

    def __update_follower_timelines(self, timestamp,\
                                    action, current, target, addition):
        table_name = TableNameGenerator.person_followed_by_person(current)
        followers = self.__cache.get_full_set(table_name)
        for each_follower in followers:
            self.__update_one_timeline(timestamp, action, each_follower,
                                       current, target, addition)

    def __update_one_timeline(self, timestamp,\
                              action, follower, current, target, addition):
        table_name = TableNameGenerator.person_timeline(follower)
        data = HistoryItem(timestamp, action, current, target, addition)
        self.__cache.prepend_list(table_name, data.encode())

