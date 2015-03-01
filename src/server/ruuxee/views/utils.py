#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

import ruuxee
import flask
import functools

def signin_required_web(f):
    """def signin_required(f): -> None

    A decorator to check user signin before running anything. If
    authentication fails, it returns unified error message.
    """
    @functools.wraps(f)
    def signin_checker(*args, **kwargs):
        session = ruuxee.Application.current_session_manager()
        success = session.validate(flask.request)
        if not success: # Failed to authenticate.
            resp = flask.jsonify(status_code=ruuxee.httplib.UNAUTHORIZED)
            resp.status_code = ruuxee.httplib.UNAUTHORIZED
            return resp
        else:
            return f(*args, **kwargs)
    return signin_checker

