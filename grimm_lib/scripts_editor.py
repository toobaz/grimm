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

from gi.repository import Gdk, Gtk, Pango, GtkSource
from cStringIO import StringIO
import sys
import traceback
import code

class GrimmScriptsEditor(Gtk.Box):
    lm = GtkSource.LanguageManager.get_default()
    lang = lm.get_language( "python" )
    
    def __init__(self, grimm_instance):
        Gtk.Box.__init__( self )
        
        self.set_orientation( Gtk.Orientation.VERTICAL )
        self.ui = grimm_instance.ui
        self.locals = grimm_instance.context
        self.shell = grimm_instance.python_shell
        
        self.pack_start( self.ui.scripts_bar, False, False, 0 )
        self.pack_start( self.ui.scripts_book, True, True, 0 )
        
        buff = GtkSource.Buffer()
        buff.set_language( self.lang )
        view = GtkSource.View(buffer=buff)
        self.ui.scripts_book.append_page( view, Gtk.Label( "New script" ) )
        self.ui.run_script.connect( "activate", self.run_script )
    
    def run_script(self, *args):
        active_index = self.ui.scripts_book.get_current_page()
        active_view = self.ui.scripts_book.get_nth_page( active_index )
        active_buffer = active_view.get_buffer()
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
