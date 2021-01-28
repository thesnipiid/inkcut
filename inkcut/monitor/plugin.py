# -*- coding: utf-8 -*-
"""
Copyright (c) 2019, Jairus Martin.

Distributed under the terms of the GPL v3 License.

The full license is in the file LICENSE, distributed with this software.

Created on Feb 2, 2019

@author: jrm
"""
import logging
from atom.api import Bool, ContainerList, Str
from inkcut.core.api import Plugin


class MonitorPlugin(Plugin):
    #Add to driver
    add_newline = Bool(True).tag(config=True)
    strip_whitespace = Bool(False).tag(config=True)
    input_enabled = Bool(True).tag(config=True)
    output_enabled = Bool(True).tag(config=True)
    autoscroll = Bool(True).tag(config=True)

    #: Command history
    history = ContainerList(Str()).tag(config=True)
