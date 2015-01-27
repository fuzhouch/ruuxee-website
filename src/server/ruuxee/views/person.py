#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"A page to represent user information."
import ruuxee
import flask

page = ruuxee.View('person')

@page.route('/<person_id>')
def get_person_info(person_id):
    """def get_person_info(person_id)

    Get web page of person information. This is a page that does not
    require signin.
    """
    dataaccess = flask.current_app.config["RUUXEE_DATA_ACCESS"]
    fields = ["name", "visible_id", "readable_id", "company"]
    data = None
    try:
        check_id = int(person_id)
        data = dataaccess.query_person('visible_id', check_id, fields)
    except Exception: # Invalid visible ID, try user ID again.
        data = dataaccess.query_person('readable_id', person_id, fields)
    if data is None: # Data not found.
        return flask.render_template('person.html')
    assert len(data) == 1
    # TODO: Not complete. We need to pass all values here.
    return flask.render_template('person.html', \
                                 name=data[0]["name"], \
                                 readable_id=data[0]["readable_id"], \
                                 visible_id=data[0]["visible_id"],
                                 company=data[0]["company"])
