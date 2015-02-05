#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"This module defines Ruuxee's web v1 API."
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
    dataaccess = ruuxee.Application.current_data_access()
    data = dataaccess.get_person_brief(person_id)
    return make_json_response(data)

@page.route('/post-brief/<post_visible_id>')
@signin_required
def get_post_brief(post_visible_id):
    """def get_post_brief(post_visible_id): -> Json

    Return a brief of specified post, including title, author, etc.
    """
    dataaccess = ruuxee.Application.current_data_access()
    data = dataaccess.get_post_brief(post_visible_id)
    return make_json_response(data)

@page.route('/post/<post_visible_id>')
@signin_required
def get_post(post_visible_id):
    """def get_post(post_visible_id): -> Json

    Return a full content of given post.
    """
    dataaccess = ruuxee.Application.current_data_access()
    return make_json_response(dataaccess.get_post(post_visible_id))

@page.route('/follow/topic/<topic_visible_id>', methods=['POST'])
@signin_required
def follow_topic(topic_visible_id):
    """def follow_topic(topic_visible_id): -> Json

    Make current person follow a topic, specified by visible ID.
    """
    # To be implemented: We don't actually know the meaning of topic for
    # now.
    dataaccess = ruuxee.Application.current_data_access()
    return make_json_response(dataaccess.follow_topic(topic_visible_id))

@page.route('/unfollow/topic/<topic_visible_id>', methods=['POST'])
@signin_required
def unfollow_topic(topic_visible_id):
    """def unfollow_topic(topic_visible_id): -> Json

    Make current person unfollow a topic, specified by visible ID.
    """
    # TODO
    # To be implemented: We don't actually know the meaning of topic for
    # now.
    dataaccess = ruuxee.Application.current_data_access()
    return make_json_response(dataaccess.unfollow_topic(topic_visible_id))

@page.route('/follow/person/<follow_person_id>', methods=['POST'])
@signin_required
def follow_person(follow_person_id):
    """def follow_person(follow_person_id): -> Json

    Make current person follow another, specified by visible ID.
    """
    dataaccess = ruuxee.Application.current_data_access()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = dataaccess.follow_person(this_person_id, follow_person_id)
    return make_json_response(resp)

@page.route('/unfollow/person/<unfollow_person_id>', methods=['POST'])
@signin_required
def unfollow_person(unfollow_person_id):
    """def unfollow_person(unfollow_person_id): -> Json

    Make current person unfollow another, specified by visible ID.
    """
    dataaccess = ruuxee.Application.current_data_access()
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_visible_id()
    resp = dataaccess.unfollow_person(this_person_id, unfollow_person_id)
    return make_json_response(resp)


@page.route('/upvote/post/<post_visible_id>', methods=['POST'])
@signin_required
def upvote_post(post_visible_id):
    """def upvote_post(post_visible_id): -> Json

    Make current person upvote a post, specified by visible ID.
    """
    dataaccess = ruuxee.Application.current_data_access()
    return make_json_response(dataaccess.upvote_post(post_visible_id))

@page.route('/unupvote/post/<post_visible_id>', methods=['POST'])
@signin_required
def unupvote_post(post_visible_id):
    """def unupvote_post(post_visible_id): -> Json

    Make current person un-upvote a post, specified by visible ID.
    """
    dataaccess = ruuxee.Application.current_data_access()
    return make_json_response(dataaccess.unupvote_post(post_visible_id))

@page.route('/downvote/post/<post_visible_id>', methods=['POST'])
@signin_required
def downvote_post(post_visible_id):
    """def downvote_post(post_visible_id): -> Json

    Make current person downvote a post, specified by visible ID.
    """
    dataaccess = ruuxee.Application.current_data_access()
    return make_json_response(dataaccess.downvote_post(post_visible_id))

@page.route('/undownvote/post/<post_visible_id>', methods=['POST'])
@signin_required
def undownvote_post(post_visible_id):
    """def undownvote_post(post_visible_id): -> Json

    Make current person downvote a post, specified by visible ID.
    """
    dataaccess = ruuxee.Application.current_data_access()
    return make_json_response(dataaccess.undownvote_post(post_visible_id))

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
    dataaccess = ruuxee.Application.current_data_access()
    data = dataaccess.add_post_under_topic(topic_visible_id)
    return make_json_response(data)

@page.route('/edit/post/<post_visible_id>', methods=['POST'])
@signin_required
def edit_post(post_visible_id):
    """def edit_post(post_visible_id): -> Json

    Make current person edit a post, specified by post visible ID. A
    person can only edit a post written by himself/herself.
    """
    dataaccess = ruuxee.Application.current_data_access()
    return make_json_response(dataaccess.edit_post(post_visible_id))

@page.route('/delete/post/<post_visible_id>', methods=['POST'])
@signin_required
def delete_post(post_visible_id):
    """def delete_post(post_visible_id): -> Json

    Make current person delete a post, specified by post visible ID. A
    person can only edit a post written by himself/herself.
    """
    dataaccess = ruuxee.Application.current_data_access()
    return make_json_response(dataaccess.delete_post(post_visible_id))

@page.route('/add/comment/post/<post_visible_id>', methods=['PUT'])
@signin_required
def add_comment_under_post(post_visible_id):
    """def add_comment_under_post(post_visible_id):

    Add a comment under specified post.
    """
    dataaccess = ruuxee.Application.current_data_access()
    data = dataaccess.add_comment_under_post(post_visible_id)
    return make_json_response(data)

@page.route('/delete/comment/<comment_visible_id>', methods=['POST'])
@signin_required
def delete_comment(comment_visible_id):
    """def delete_comment(comment_visible_id):

    Delete a specified comment. A person can only delete a comment
    written by himself/herself.
    """
    dataaccess = ruuxee.Application.current_data_access()
    data = dataaccess.delete_comment(comment_visible_id)
    return make_json_response(data)

@page.route('/timeline/updates/<last_item_id>', methods=['GET'])
@signin_required
def get_timeline_updates(last_item_id):
    """def get_timeline_updates(last_item_id): -> Json

    Get latest updates of current timeline. It retrieves only the items
    later than speicified item ID.
    """
    dataaccess = ruuxee.Application.current_data_access()
    data = dataaccess.delete_comment(comment_visible_id)
    return make_json_response(data)
