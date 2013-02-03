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
