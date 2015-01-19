#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"A page to represent user information."
import ruuxee

page = ruuxee.View('person')

# TODO: Page handlers

@page.route('/<name>')
def get_person_info(name):
    pass
