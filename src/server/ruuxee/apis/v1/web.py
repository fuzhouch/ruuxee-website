#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"This module defines Ruuxee's web v1 API."
import ruuxee
import flask
import functools

page = ruuxee.View('web')

def signin_required(f):
    """def signin_required(f): -> None

    A decorator to check user signin before running anything. If
    authentication fails, it returns unified error message.
    """
    @functools.wraps(f)
    def signin_checker(*args, **kwargs):
        session = flask.current_app.config["RUUXEE_SESSION_MANAGER"]
        success = session.validate(flask.request)
        if not success: # Failed to authenticate.
            resp = flask.jsonify(status_code=ruuxee.httplib.UNAUTHORIZED)
            resp.status_code = ruuxee.httplib.UNAUTHORIZED
            return resp
        else:
            return f(*args, **kwargs)
    return signin_checker

@page.route('/person-brief/<person_visible_id>')
@signin_required
def get_person_brief(person_visible_id):
    """def get_person_brief(person_visible_id): -> Json

    Return a brief of specified person, including name, company, city,
    follow-unfollow relationship, etc.
    """
    dataaccess = flask.current_app.config["RUUXEE_DATA_ACCESS"]
    session = flask.current_app.config["RUUXEE_SESSION_MANAGER"]
    # Brief information contains only the following fields. They are
    # supposed to be used in hovering popup window.
    visible_id = session.last_authenticated_person_visible_id()
    fields = ["name", "visible_id"]
    data = dataaccess.query_person('visible_id', visible_id, fields)
    if data is None: # Data not found.
        resp = flask.jsonify(status_code=ruuxee.httplib.BAD_REQUEST)
        resp.status_code = ruuxee.httplib.BAD_REQUEST
        return resp
    assert len(data) == 1
    return flask.jsonify(status_code=ruuxee.httplib.OK, \
                         name=data[0]["name"],\
                         visible_id=data[0]["visible_id"])

@page.route('post-brief/<post_visible_id>')
def get_post_brief(post_visible_id):
    """def get_post_brief(post_visible_id): -> Json

    Return a brief of specified post, including title, author, etc.
    """
    pass

@page.route('post/<post_visible_id>')
def get_post(post_visible_id):
    """def get_post(post_visible_id): -> Json

    Return a full content of given post.
    """
    pass

@page.route('/follow/topic/<topic_visible_id>', methods=['POST'])
def follow_topic(topic_visible_id):
    """def follow_topic(topic_visible_id): -> Json

    Make current person follow a topic, specified by visible ID.
    """
    pass

@page.route('/unfollow/topic/<topic_visible_id>', methods=['POST'])
def unfollow_topic(topic_visible_id):
    """def unfollow_topic(topic_visible_id): -> Json

    Make current person unfollow a topic, specified by visible ID.
    """
    pass

@page.route('/follow/person/<person_visible_id>', methods=['POST'])
def follow_person(person_visible_id):
    """def follow_person(person_visible_id): -> Json

    Make current person follow another, specified by visible ID.
    """
    pass

@page.route('/unfollow/person/<person_visible_id>', methods=['POST'])
def unfollow_person(person_visible_id):
    """def unfollow_person(person_visible_id): -> Json

    Make current person unfollow another, specified by visible ID.
    """
    pass

@page.route('/upvote/post/<post_visible_id>', methods=['POST'])
def upvote_post(post_visible_id):
    """def upvote_post(post_visible_id): -> Json

    Make current person upvote a post, specified by visible ID.
    """
    pass

@page.route('/unupvote/post/<post_visible_id>', methods=['POST'])
def unupvote_post(post_visible_id):
    """def unupvote_post(post_visible_id): -> Json

    Make current person un-upvote a post, specified by visible ID.
    """
    pass

@page.route('/downvote/post/<post_visible_id>', methods=['POST'])
def downvote_post(post_visible_id):
    """def downvote_post(post_visible_id): -> Json

    Make current person downvote a post, specified by visible ID.
    """
    pass

@page.route('/undownvote/post/<post_visible_id>', methods=['POST'])
def undownvote_post(post_visible_id):
    """def undownvote_post(post_visible_id): -> Json

    Make current person downvote a post, specified by visible ID.
    """
    pass

@page.route('/add/post/topic/<topic_visible_id>', methods=['PUT'])
def add_post_under_topic(topic_visible_id):
    """def add_post_under_topic(topic_visible_id): -> Json

    Make current person add a new post under topic. The content of post
    is attached in HTML body.
    """
    pass

@page.route('/edit/post/<post_visible_id>', methods=['POST'])
def edit_post(post_visible_id):
    """def edit_post(post_visible_id): -> Json

    Make current person edit a post, specified by post visible ID. A
    person can only edit a post written by himself/herself.
    """
    pass

@page.route('/delete/post/<post_visible_id>', methods=['POST'])
def delete_post(post_visible_id):
    """def delete_post(post_visible_id): -> Json

    Make current person delete a post, specified by post visible ID. A
    person can only edit a post written by himself/herself.
    """
    pass

@page.route('/add/comment/post/<post_visible_id>', methods=['PUT'])
def add_comment_under_post(post_visible_id):
    """def add_comment_under_post(post_visible_id):

    Add a comment under specified post.
    """
    pass

@page.route('/delete/comment/<comment_visible_id>', methods=['POST'])
def delete_comment(comment_visible_id):
    """def delete_comment(comment_visible_id):

    Delete a specified comment. A person can only delete a comment
    written by himself/herself.
    """
    pass

@page.route('/timeline/updates/<last_item_id>', methods=['GET'])
def get_timeline_updates(last_item_id):
    """def get_timeline_updates(last_item_id): -> Json

    Get latest updates of current timeline. It retrieves only the items
    later than speicified item ID.
    """
    pass
