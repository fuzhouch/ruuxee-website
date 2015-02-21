#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"""A configuration to setup enviornment for Web UI developers.

    This environment is configured witht the following settings:
    1. Core access is fake with hardcoded fake data.
    2. Start server in debug mode.
"""

import ruuxee.models.v1.mock as mockv1
import ruuxee.models.v1 as v1

#
# For web UI developers, we use fake data to minimize configuration.
# Change it to use ruuxee.models.v1.Database and ruuxee.model.v1.Redis
# if you want to use real production data.
#
# Configuration to be used by ruuxee models.
cache = mockv1.Cache()
queue = mockv1.MessageQueue()
database = mockv1.Database(cache)
RUUXEE_CORE = v1.Core(database, cache, queue)
RUUXEE_SESSION_MANAGER = mockv1.AlwaysBourneZhuWebSession(database)

# The following configurations can only be visible in unit test mode.
# Production environment does not have them.
RUUXEE_UT_DATABASE = database
RUUXEE_UT_CACHE = cache
RUUXEE_UT_QUEUE = queue
