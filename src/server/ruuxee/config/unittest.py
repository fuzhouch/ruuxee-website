#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright @2015 by ruuxee.com, All rights reserved.

from ruuxee.config.webui_dev import *

# Use almost same setting, with only expection that we always
# authenticate current user as bourne.zhu. This is because the
# NoPasswordCheckSession() used by webui_dev required HTML form for
# check-in, which is difficult to be done in unittest.
RUUXEE_SESSION_MANAGER = mockv1.AlwaysBourneZhuWebSession(database)
