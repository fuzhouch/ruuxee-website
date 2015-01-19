#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"A page to represent a timeline of given user."
import ruuxee

page = ruuxee.View('timeline')

# TODO: Page handlers

@page.route('/')
@page.route('/timeline')
def get_timeline(name):
    pass
