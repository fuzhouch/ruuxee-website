#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"""A configuration to setup enviornment for Web UI developers.

    This environment is configured witht the following settings:
    1. Database access is fake with hardcoded fake data.
    2. Start server in debug mode.
"""

import ruuxee.models.v1.mock as mockv1
import ruuxee.models.v1 as v1

#
# For web UI developers, we use fake data to minimize configuration.
# Change it to use ruuxee.models.v1.Database and ruuxee.model.v1.Redis
# if you want to use real production data.
#
database = mockv1.Database()
# Configuration to be used by ruuxee models.
RUUXEE_DATA_ACCESS = database
RUUXEE_SESSION_MANAGER = mockv1.AlwaysBourneZhuWebSession(database)
