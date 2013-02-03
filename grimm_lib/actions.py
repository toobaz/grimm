# -*- coding: utf-8 -*-

from gi.repository import Gtk

import pandas

actions = []

class GrimmAction(object):
    def __init__(self, grimm_instance):
        self.grimm = grimm_instance
        self.gtk_action = Gtk.Action( *self.action_fields )
        self.gtk_action.connect( "activate", self.run )

class GrimmQuit(GrimmAction):
    def run(self):
        Gtl.main_quit()

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
    action_fields = ( "OpenCsv",
                      "Open _CSV",
                      "Open CSV (Comma Separated Values)",
                      Gtk.STOCK_OPEN )
    path = "/MenuBar/FileMenu/OpenData"
    name = "OpenCsv"
        
    def do_load(self, path):
        self.grimm.df = pandas.read_csv( path )

actions.append( OpenCsv )
