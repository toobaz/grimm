# -*- coding: utf-8 -*-

from gi.repository import Gtk

import pandas

actions = []

class GrimmAction(object):
    def __init__(self, grimm_instance):
        self.grimm = grimm_instance
        self.gtk_action = Gtk.Action( self.name,
                                      self.label,
                                      self.description,
                                      self.icon )
        
        self.gtk_action.connect( "activate", self.run )

class GrimmQuit(GrimmAction):
    name = label = description = "Quit"
    icon = Gtk.STOCK_QUIT
    path = "/MenuBar/FileMenu"
    
    def run(self, *args):
        Gtk.main_quit()

class GrimmShowAbout(GrimmAction):
    def run(self):
        # TODO
        pass

class GrimmActionOpen(GrimmAction):
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
            self.do_load( path )
            self.grimm.refresh_series()

class OpenCsv(GrimmActionOpen):
    name = "OpenCsv"
    label = "Open _CSV"
    description = "Open CSV (Comma Separated Values)"
    path = "/MenuBar/FileMenu/OpenData"
    
        
    def do_load(self, path):
        self.grimm.df = pandas.read_csv( path )

actions.append( OpenCsv )
