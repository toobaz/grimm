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

"""
This is the main module for the definition of actions.

Actions are exposed iff they are subclasses of GrimmAction and have a "name"
attribute.
"""

from gi.repository import Gtk

import pandas

actions = []

class GrimmAction(object):
    icon = None
    
    def __init__(self, grimm_instance):
        self.grimm = grimm_instance
        self.gtk_action = Gtk.Action( self.name,
                                      self.label,
                                      self.description,
                                      self.icon )
        
        self.gtk_action.connect( "activate", self.run )
    
    @classmethod
    def register(cls):
        subactions = []
        if hasattr( cls, "name" ):
            subactions.append( cls )
        
        for subclass in cls.__subclasses__():
            subactions.extend( subclass.register() )
        
        return subactions

class GrimmQuit(GrimmAction):
    name = label = description = "Quit"
    icon = Gtk.STOCK_QUIT
    path = "/MenuBar/FileMenu"
    
    def run(self, *args):
        Gtk.main_quit()

class GrimmShowAbout(GrimmAction):
    name = "ShowAbout"
    label = description = "About Grimm"
    icon = Gtk.STOCK_ABOUT
    path = "/MenuBar/HelpMenu"
    
    def run(self, *args):
        # TODO
        pass

class GrimmActionOpen(GrimmAction):
    icon = Gtk.STOCK_OPEN
    def run(self, *args):
        
        fc = Gtk.FileChooserDialog()
        fc.set_action( Gtk.FileChooserAction.OPEN )
        fc.add_buttons( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK,     Gtk.ResponseType.OK )
        fc.set_default_response( Gtk.ResponseType.OK )
        
        resp = fc.run()
        fc.hide()
        if resp == Gtk.ResponseType.OK:
            path = fc.get_filenames()[0]
            self.grimm.df = self.command( path )
            self.grimm.refresh_series()
    
    def command(self, *args, **kwargs):
        meth = getattr( pandas, self.method )
        return meth( *args, **kwargs )

class OpenCsv(GrimmActionOpen):
    name = "OpenCsv"
    label = "Open _CSV"
    description = "Open CSV (Comma Separated Values)"
    path = "/MenuBar/FileMenu/OpenData"
    
    method = "read_csv"

import actions_statsmodels
import actions_matplotlib

actions = GrimmAction.register()
