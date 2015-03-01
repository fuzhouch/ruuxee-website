#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

import time
import functools
import logging
import threading

def stimestamp():
    """def stimestamp() -> Integer

    Standard timestamp function for ruuxee. Always return seconds since
    Epoch (1970-01-01, 00:00:00)
    """
    return int(time.time())

def mstimestamp():
    """def stimestamp() -> Integer

    Standard timestamp function for ruuxee. Always return milliseconds
    since Epoch (1970-01-01, 00:00:00).

    NOTE: This behavior may be different when running tests on non-UNIX
    platforms.
    """
    return int(time.time() * 1000000)

def valid_user_visible_id(visible_id):
    return True

def valid_post_visible_id(visible_id):
    return True

def valid_topic_visible_id(visible_id):
    return True

_tl = threading.local()
_tl.current_function_name = ""

class Logging():
    """
    A logging class to help simplify the logging output. For all classes
    that want to take advantage of Logging class, please inherite from
    it. See :InteractionWorker: for example.
    """
    def __init__(self):
        # Make sure __init__ does nothing so child classes does not need
        # to do anything.
        pass

    @staticmethod
    def current_function_name():
        return _tl.current_function_name

    def log_error(self, msg):
        logging.error("%s.%s: %s" % \
                (self.__class__.__name__,
                 _tl.current_function_name, msg))

    def log_warning(self, msg):
        logging.warning("%s.%s: %s" % \
                (self.__class__.__name__,
                 _tl.current_function_name, msg))

    def log_info(self, msg):
        logging.info("%s.%s: %s" % \
                (self.__class__.__name__,
                 _tl.current_function_name, msg))

    def log_debug(self, msg):
        logging.debug("%s.%s: %s" % \
                (self.__class__.__name__,
                 _tl.current_function_name, msg))

    @staticmethod
    def enter_leave(f):
        """enter_leave(f) -> decorator
        A decorator to print enter/leave logging for each function.
        """
        @functools.wraps(f)
        def enter_leave_wrap_func(*args, **kwargs):
            # Different threads will hold different _tl
            backup = None
            try:
                backup = _tl.current_function_name
            except Exception:
                # This is a different thread, we need to initialize
                # thread local data.
                _tl.current_function_name = ""
                backup = _tl.current_function_name

            _tl.current_function_name = f.__name__
            logging.debug("%s: enter" % f.__name__)
            ret = f(*args, **kwargs)
            logging.debug("%s: leave" % f.__name__)
            _tl.current_function_name = backup
            return ret
        return enter_leave_wrap_func

