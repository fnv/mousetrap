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

"""Ocvfw Global Vars."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import os

abs_path = os.path.abspath(os.path.dirname(__file__))

haar_cds = { 'Face'  :  "%s/haars/haarcascade_frontalface_alt.xml" % abs_path,
             'Eyes'  :  "%s/haars/frontalEyes35x16.xml" % abs_path,
             #'Eyes'  :  "../ocvfw/haars/haarcascade_eye_tree_eyeglasses.xml",
             'Mouth' :  "%s/haars/Mouth.xml" % abs_path}
