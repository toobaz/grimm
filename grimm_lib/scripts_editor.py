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
This module provides the scripts editor.
"""

from gi.repository import Gdk, Gtk, Pango, GtkSource, Gio
from cStringIO import StringIO
import sys
import traceback
import code
import os

class Script(Gtk.ScrolledWindow):
    uri = ''
    lm = GtkSource.LanguageManager.get_default()
    lang = lm.get_language( "python" )
    def __init__(self, uri=None, name=None):
        Gtk.ScrolledWindow.__init__( self )
        self.buffer = GtkSource.Buffer()
        self.buffer.set_language( self.lang )
        self.view = GtkSource.View( buffer=self.buffer )
        self.add( self.view )
        if uri:
            self.file = Gio.File.new_for_uri( uri )
            name = self.file.get_basename()
            
            # Reading from streams does not work currently:
            # stream = self.file.read( None )
            
            path = self.file.get_path()
            self.fop = open( path )
            
            self.buffer.set_text( self.fop.read() )
            self.fop.close()
        else:
            self.file = None
        self.name = name
        self.label = Gtk.Label( name )
        self.show_all()
    
    def change_uri(self, uri):
        self.file = Gio.File.new_for_uri( uri )
        name = self.file.get_basename()
        self.label.set_text( name )
    
    def save(self):
        path = self.file.get_path()
        fout = open( path, 'w' )
        fout.write( self.text() )
        fout.close()
    
    def text(self):
        start, end = self.buffer.get_bounds()
        text = self.buffer.get_text( start, end, False )
        return text        

class GrimmScriptsEditor(Gtk.Box):
    def __init__(self, grimm_instance):
        Gtk.Box.__init__( self )
        
        self.set_orientation( Gtk.Orientation.VERTICAL )
        self.ui = grimm_instance.ui
        self.locals = grimm_instance.context
        self.shell = grimm_instance.python_shell
        
        self.pack_start( self.ui.scripts_bar, False, False, 0 )
        self.pack_start( self.ui.scripts_book, True, True, 0 )
        
        self.opened_scripts = set()
        
        for thing in ("new", "open", "save", "save_as", "run", "close"):
            full_thing = "script_%s" % thing
            action = getattr( self.ui, full_thing )
            callback = getattr( self, full_thing )
            action.connect( "activate", callback )
        
        self.script_new()
    
    def script_new(self, *args):
        i = 0
        while True:
            label = "Unsaved script %d" % i
            if label not in [s.name for s in self.ui.scripts_book.get_children()]:
                break
            i += 1
        
        script = Script( name=label )
        
        self.opened_scripts.add( script )
        
        self.ui.scripts_book.append_page( script, script.label )
        index = self.ui.scripts_book.page_num( script.view )
        self.ui.scripts_book.set_current_page( index )
    
    def script_open(self, *args):
        resp = self.ui.script_fileopener.run()
        self.ui.script_fileopener.hide()
        if resp == Gtk.ResponseType.OK:
            # If there's an open dummy one, close it:
            if self.ui.scripts_book.get_n_pages() == 1:
                cur_script = self.ui.scripts_book.get_nth_page( 0 )
                if not cur_script.text() and not cur_script.file:
                    self.script_close()
            
            script = Script( self.ui.script_fileopener.get_uri() )
            self.ui.scripts_book.append_page( script, script.label )
            index = self.ui.scripts_book.page_num( script.view )
            self.ui.scripts_book.set_current_page( index )
    
    def script_save(self, *args):
        active_index = self.ui.scripts_book.get_current_page()
        active_script = self.ui.scripts_book.get_nth_page( active_index )
        if active_script.file:
            active_script.save()
        else:
            self.script_save_as(self, *args)
    
    def script_save_as(self, *args):
        active_index = self.ui.scripts_book.get_current_page()
        active_script = self.ui.scripts_book.get_nth_page( active_index )
        resp = self.ui.script_filesaver.run()
        self.ui.script_filesaver.hide()
        if resp == Gtk.ResponseType.OK:
            new_uri = self.ui.script_filesaver.get_uri()
            active_script.change_uri( new_uri )
            active_script.save()
    
    def script_run(self, *args):
        active_index = self.ui.scripts_book.get_current_page()
        active_script = self.ui.scripts_book.get_nth_page( active_index )
        active_buffer = active_script.buffer
        start, end = active_buffer.get_bounds()
        script = active_buffer.get_text( start, end, False )
        
        # Not using ast because it would need the whole input to be valid.
        block = ""
        for line in script.splitlines():
            block += line + '\n'
            try:
                valid = code.compile_command( block )
            except SyntaxError:
                self.shell.print_error( block )
                break
            if valid:
                # Prevent newlines from causing empty prompts:
                if block.strip():
                    self.shell.run_command( block, valid )
                block = ""
    
    def script_close(self, *args):
        active_index = self.ui.scripts_book.get_current_page()
        active_script = self.ui.scripts_book.get_nth_page( active_index )
        self.ui.scripts_book.remove_page( active_index )
