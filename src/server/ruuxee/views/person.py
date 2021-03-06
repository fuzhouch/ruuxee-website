#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"A page to represent user information."
import ruuxee
import flask
import ruuxee.views.utils as vutils

page = ruuxee.View("person")

@page.route('/<person_id>')
def get_person_info(person_id):
    """def get_person_info(person_id)

    Get web page of person information. This is a page that does not
    require signin.
    """
    core = ruuxee.Application.current_core()
    data = core.get_person_brief(person_id)
    if data is None: # Data not found.
        return flask.render_template('person.html')
    return flask.render_template('person.html', **data)

