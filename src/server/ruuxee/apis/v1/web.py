#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"""
This module defines Ruuxee's web v1 API. The whole feature is
implemented as a Flask Blueprint.

Following Flask coding practice, it exposes one global object, page,
which is the main entry point of all features.

The Blueprint is configurable via ruuxee.Application. The main interface
is available in two helper functions in ruuxee.Appliaction:

    >>> ruuxee.Application.current_session_manager()
    >>> ruuxee.Application.current_core()

So the API can actually be configured to behave like a web API or
mobile app API, if the application is properly configured with different
Core and SessionManager.
"""
import ruuxee
import flask
import functools

page = ruuxee.View('web')

# ==== Helper functions ===
def make_json_response(data):
    """def make_json_response(data) -> flask.Response(json_blob)

    This is a helper function when returning objects.
    """
    if data is None: # Data not found.
        resp = flask.jsonify(status_code=ruuxee.httplib.BAD_REQUEST)
        resp.status_code = ruuxee.httplib.BAD_REQUEST
        resp.content_encoding = 'utf-8'
    elif "status_code" in data:
        resp = flask.jsonify(**data)
        resp.status_code = data["status_code"]
        resp.content_encoding = 'utf-8'
    else:
        resp = flask.jsonify(status_code=ruuxee.httplib.OK, **data)
        resp.content_encoding = 'utf-8'
    return resp

def signin_required(f):
    """def signin_required(f): -> None

    A decorator to check user signin before running anything. If
    authentication fails, it returns unified error message.
    """
    @functools.wraps(f)
    def signin_checker(*args, **kwargs):
        session = ruuxee.Application.current_session_manager()
        success = session.validate(flask.request)
        if not success: # Failed to authenticate.
            print("HERE!")
            resp = flask.jsonify(status_code=ruuxee.httplib.UNAUTHORIZED)
            resp.status_code = ruuxee.httplib.UNAUTHORIZED
            return resp
        else:
            return f(*args, **kwargs)
    return signin_checker

# ==== Api handlers ===
@page.route('/person-brief/<person_id>')
@signin_required
def get_person_brief(person_id):
    """def get_person_brief(person_id): -> Json

    Return a brief of specified person, including name, company, city,
    follow-unfollow relationship, etc.

    The function accepts both visible ID and/or readable ID of user as
    input.
    """
    core = ruuxee.Application.current_core()
    data = core.get_person_brief(person_id)
    return make_json_response(data)

@page.route('/topic-brief/<topic_visible_id>')
@signin_required
def get_topic_brief(topic_visible_id):
    """def get_topic_brief(topic_visible_id): -> Json

    Return a brief of specific topic."""
    core = ruuxee.Application.current_core()
    data = core.get_topic_brief(topic_visible_id)
    return make_json_response(data)

@page.route('/post-brief/<post_visible_id>')
@signin_required
def get_post_brief(post_visible_id):
    """def get_post_brief(post_visible_id): -> Json

    Return a brief of specified post, including title, author, etc.
    """
    core = ruuxee.Application.current_core()
    data = core.get_post_brief(post_visible_id)
    return make_json_response(data)

@page.route('/post/<post_visible_id>')
@signin_required
def get_post(post_visible_id):
    """def get_post(post_visible_id): -> Json

    Return a full content of given post.
    """
    core = ruuxee.Application.current_core()
    return make_json_response(core.get_post(post_visible_id))

@page.route('/follow/topic/<topic_visible_id>', methods=['POST'])
@signin_required
def follow_topic(topic_visible_id):
    """def follow_topic(topic_visible_id): -> Json

    Make current person follow a topic, specified by visible ID.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.follow_topic(this_person_id, topic_visible_id)
    return make_json_response(resp)

@page.route('/unfollow/topic/<topic_visible_id>', methods=['POST'])
@signin_required
def unfollow_topic(topic_visible_id):
    """def unfollow_topic(topic_visible_id): -> Json

    Make current person unfollow a topic, specified by visible ID.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.unfollow_topic(this_person_id, topic_visible_id)
    return make_json_response(resp)

@page.route('/follow/person/<follow_person_id>', methods=['POST'])
@signin_required
def follow_person(follow_person_id):
    """def follow_person(follow_person_id): -> Json

    Make current person follow another, specified by visible ID.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.follow_person(this_person_id, follow_person_id)
    return make_json_response(resp)

@page.route('/unfollow/person/<unfollow_person_id>', methods=['POST'])
@signin_required
def unfollow_person(unfollow_person_id):
    """def unfollow_person(unfollow_person_id): -> Json

    Make current person unfollow another, specified by visible ID.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.unfollow_person(this_person_id, unfollow_person_id)
    return make_json_response(resp)

@page.route('/upvote/post/<post_visible_id>', methods=['POST'])
@signin_required
def upvote_post(post_visible_id):
    """def upvote_post(post_visible_id): -> Json

    Make current person upvote a post, specified by visible ID.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.upvote_post(this_person_id, post_visible_id)
    return make_json_response(resp)

@page.route('/downvote/post/<post_visible_id>', methods=['POST'])
@signin_required
def downvote_post(post_visible_id):
    """def downvote_post(post_visible_id): -> Json

    Make current person downvote a post, specified by visible ID.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.downvote_post(this_person_id, post_visible_id)
    return make_json_response(resp)

@page.route('/neutralize/post/<post_visible_id>', methods=['POST'])
@signin_required
def neutralize_post(post_visible_id):
    """def neutralize_post(post_visible_id): -> Json

    Make current person neutralize a post, specified by visible ID.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.neutralize_post(this_person_id, post_visible_id)
    return make_json_response(resp)

@page.route('/add/post/topic/<topic_visible_id>', methods=['PUT'])
@signin_required
def add_post_under_topic(topic_visible_id):
    """def add_post_under_topic(topic_visible_id): -> Json

    Make current person add a new post under topic. The content of post
    is attached in HTML body.
    """
    # TODO
    # To be implemented: We don't actually know the meaning of topic for
    # now.
    core = ruuxee.Application.current_core()
    data = core.add_post_under_topic(topic_visible_id)
    return make_json_response(data)

@page.route('/edit/post/<post_visible_id>', methods=['POST'])
@signin_required
def edit_post(post_visible_id):
    """def edit_post(post_visible_id): -> Json

    Make current person edit a post, specified by post visible ID. A
    person can only edit a post written by himself/herself.
    """
    core = ruuxee.Application.current_core()
    return make_json_response(core.edit_post(post_visible_id))

@page.route('/delete/post/<post_visible_id>', methods=['POST'])
@signin_required
def delete_post(post_visible_id):
    """def delete_post(post_visible_id): -> Json

    Make current person delete a post, specified by post visible ID. A
    person can only edit a post written by himself/herself.
    """
    core = ruuxee.Application.current_core()
    return make_json_response(core.delete_post(post_visible_id))

@page.route('/add/comment/post/<post_visible_id>', methods=['PUT'])
@signin_required
def add_comment_under_post(post_visible_id):
    """def add_comment_under_post(post_visible_id):

    Add a comment under specified post.
    """
    core = ruuxee.Application.current_core()
    data = core.add_comment_under_post(post_visible_id)
    return make_json_response(data)

@page.route('/delete/comment/<comment_visible_id>', methods=['POST'])
@signin_required
def delete_comment(comment_visible_id):
    """def delete_comment(comment_visible_id):

    Delete a specified comment. A person can only delete a comment
    written by himself/herself.
    """
    core = ruuxee.Application.current_core()
    data = core.delete_comment(comment_visible_id)
    return make_json_response(data)

@page.route('/timeline/range/<begin>/<end>', methods=['GET'])
@signin_required
def get_timeline_range(begin, end):
    """def get_timeline_range(begin, end): -> Json

    Get a range of latest updates of current timeline, with offset
    [begin, end). The latest update always starts from 0.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.get_timeline_range(this_person_id, begin, end)
    return make_json_response(resp)

@page.route('/notification/range/<begin>/<end>', methods=['GET'])
@signin_required
def get_notification_range(begin, end):
    """def get_notification_range(begin, end): -> Json

    Get a range of latest updates of notifications, with offset
    [begin, end). The latest update always starts from 0.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.get_notification_range(this_person_id, begin, end)
    return make_json_response(resp)

@page.route('/timeline/update/<since_timestamp>', methods=['GET'])
@signin_required
def get_timeline_update(since_timestamp):
    """def get_timeline_updates(since_timestamp): -> Json

    Get a range of latest updates of timeline later than given
    timestamp.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.get_timeline_update(this_person_id, since_timestamp)
    return make_json_response(resp)

@page.route('/notification/update/<since_timestamp>', methods=['GET'])
@signin_required
def get_notification_update(since_timestamp):
    """def get_notification_updates(since_timestamp): -> Json

    Get a range of latest updates of notifications later than given
    timestamp.
    """
    core = ruuxee.Application.current_core()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = core.get_notification_update(this_person_id, since_timestamp)
    return make_json_response(resp)

