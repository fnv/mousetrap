# -*- coding: utf-8 -*-

# Ocvfw
#
# Copyright 2009 Flavio Percoco Premoli
#
# This file is part of Ocvfw.
#
# Ocvfw is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v2 as published
# by the Free Software Foundation.
#
# Ocvfw is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ocvfw.  If not, see <http://www.gnu.org/licenses/>>.


"""Python Opencv Handler."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import os
import re

def get_idm(idm):
    """
    Returns the idm's class instance.

    Arguments:
    - idm: The requested idm.
    """
    return __import__("ocvfw.idm.%s" % idm,
                      globals(),
                      locals(),
                      [''])

def get_idms_list():
    reg = re.compile(r'([A-Za-z0-9]+)\.py$', re.DOTALL)
    dirname = os.path.dirname(__file__)
    return [ mod[0] for mod in [ reg.findall(f) for f in os.listdir("%s/idm/" % dirname)] if mod ]

def get_idm_inf(idm):
    tmp = __import__("ocvfw.idm.%s" % idm,
                      globals(),
                      locals(),
                      [''])
    return { "name" : tmp.a_name, "dsc" : tmp.a_description, "stgs" : tmp.a_settings}

