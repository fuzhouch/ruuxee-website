#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.
"""A configuration to setup enviornment for Web UI developers.

    This environment is configured witht the following settings:
    1. Database access is fake with hardcoded fake data.
    2. Start server in debug mode.
"""

class FakeSql(object):
    pass
class FakeRedis(object):
    pass
class FakeAuth(object):
    pass

DATABASE = FakeSql()
MEMCACHE = FakeRedis()
AUTH = FakeAuth()
