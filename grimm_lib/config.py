# -*- coding: utf-8 -*-
# grimm
#
# grimm is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# grimm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with grimm; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# Copyright © 2013 Pietro Battiston <me@pietrobattiston.it>

import sys, os
from os import path
from xdg.BaseDirectory import xdg_config_home, xdg_data_home

"""
This module takes care of finding configs and data.
It is not specific to grimm, but it does assume a given structure
("APP_NAME.svg" in the "stuff" folder).
"""

APP_NAME = 'grimm'

########################## CONFIGURATION #######################################

not_installed_dir = path.realpath( path.dirname( path.dirname( __file__ ) ) )
if path.exists( not_installed_dir + '/stuff/%s.svg' % APP_NAME ):
    STUFF_DIR = not_installed_dir + '/stuff'
    LOCALE_DIR = not_installed_dir + '/locale'
else:
    for directory in [sys.prefix, sys.prefix + '/local']:
        installed_root_dir = directory + '/share'
        if path.exists( installed_root_dir + '/%s/stuff' % APP_NAME ):
            STUFF_DIR = installed_root_dir + '/%s/stuff' % APP_NAME
            LOCALE_DIR = installed_root_dir + '/locale'
            break

########################## END OF CONFIGURATION ################################

CONFIG_DIR = path.join( xdg_config_home, APP_NAME )
DATA_DIR = path.join( xdg_data_home, APP_NAME )
