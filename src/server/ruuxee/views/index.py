#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"A page set to represent main pages."
import ruuxee
import ruuxee.views.utils as vutils
import flask

page = ruuxee.View("index")

@page.route("/", methods=["GET"])
def index():
    return flask.redirect(flask.url_for("index.timeline"))

@page.route("/timeline", methods=["GET"])
def get_timeline():
    # TODO
    # I haven't implemented a complete timeline page so I use
    # person page as a replacement. Will change in the future.
    session = ruuxee.Application.current_session_manager()
    this_person_id = session.authenticated_person_readable_id()
    return flask.redirect(flask.url_for("person.get_person_info",
                                        person_id=this_person_id))

@page.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        session = ruuxee.Application.current_session_manager()
        success = session.validate(flask.request)
        if not success:
            return flask.redirect(flask.url_for("/login"))
    elif flask.request.method == "GET":
        return flask.render_template("login.html")
    return flask.redirect(flask.url_for("index.get_timeline"))

@page.route("/logout", methods=["GET", "POST"])
def logout():
    session = ruuxee.Application.current_session_manager()
    session.logout(request)
    return flask.redirect(flask.url_for("index.login"))

