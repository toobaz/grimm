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
# Copyright © 2008-2009  Christian Hammond
# Copyright © 2008-2009  David Trowbridge
# Copyright © 2013 Pietro Battiston <me@pietrobattiston.it>

"""
This module provides the Python interactive shell.

It is an almost straightforward port to Python of python-shell.c, from project
gtk-parasite, git revision 0a0c90b7098d8c5b8bc06ecc88459520ad533601, from
November 2012.
"""

from gi.repository import Gdk, Gtk, Pango
from cStringIO import StringIO
import sys
import traceback

class GrimmPythonShell(Gtk.ScrolledWindow):
    def __init__(self, grimm_instance):
        Gtk.ScrolledWindow.__init__( self )
        
        self.history = ['']
        self.hist_cursor = -1
        self.locals = {}
        
        self.in_block = False
        self.pending_command = ''
        
        self.ui = grimm_instance.ui
        
        self.add( self.ui.shell_view )
        
        fontdesc = Pango.FontDescription( "monospace" )
        self.ui.shell_view.modify_font( fontdesc )
        
        self.ui.shell_view.set_cursor_visible( True )
        self.ui.shell_view.set_pixels_above_lines( 3 )
        self.ui.shell_view.set_left_margin( 3 )
        self.ui.shell_view.set_right_margin( 3 )
        self.ui.shell_view.set_size_request( 500, 500 )
        
        # Initialize with gravity values:
        self.marks = { "scroll" : False, "line_start" : True }
        end_iter = self.ui.shell.get_end_iter()
        for name, grav in self.marks.items():
            self.marks[name] = self.ui.shell.create_mark( name, end_iter, grav )
        
        self.ui.shell.create_tag( "stdout" )
        self.ui.shell.create_tag( "stderr",
                                  foreground="red",
                                  paragraph_background="#FFFFE0" )
        self.ui.shell.create_tag( "prompt",
                                  foreground="blue" )
        
        self.ui.shell_view.connect( "key_press_event", self.key_press_cb )
        
        self.write_prompt()
    
    def write_prompt(self):
        prompt = "... " if self.pending_command else ">>> "
        self.append_text( prompt, "prompt" )
        end_iter = self.ui.shell.get_end_iter()
        self.ui.shell.move_mark( self.marks["line_start"], end_iter )
    
    def process_line(self):
        
        command = self.get_input()
        
        self.append_text( "\n", "stdout" )
        
        if command:
            self.history.insert( 0, command )
            self.cur_history_index = -1
        
        last_char = command[-1]
        if last_char in (":", "\\")\
        or (self.in_block and last_char in (' ', '\t')):
            if not self.pending_command:
                self.pending_command = "\n"
            else:
                self.pending_command += ("%s\n" % command)
            
            if last_char == ':':
                self.in_block = True
        
        else:
            if self.pending_command:
                self.pending_command +=  ("%s\n" % command)
        
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()
            
            dict_loc = {}
            dict_glob = {}
            try:
                try:
                    result = eval( command, globals(), self.locals )
                    out = "%s\n" % result
                except SyntaxError:
                    exec( command, globals(), self.locals )
                    out = redirected_output.getvalue()
                self.append_text( out, "stdout" )
            except:
                self.append_text( "".join( traceback.format_exc() ), "stderr" )
            
            sys.stdout = old_stdout
            
            if self.pending_command:
                self.pending_command = ''
                self.in_block = False
        
        self.write_prompt()
    
    def replace_input(self, text):
        start = self.ui.shell.get_iter_at_mark( self.marks["line_start"] )
        end = self.ui.shell.get_end_iter()
        
        self.ui.shell.delete( start, end )
        self.ui.shell.insert( end, text )
    
    def get_input(self):
        start_iter = self.ui.shell.get_iter_at_mark( self.marks["line_start"] )
        end_iter = self.ui.shell.get_end_iter()
        
        return self.ui.shell.get_text( start_iter, end_iter, False )
    
    def history_back(self):
        if self.cur_history_index == -1:
            if self.history:
                self.cur_history_index = 0
            else:
                return ""
        elif len( self.history ) > self.cur_history_index + 2:
            self.cur_history_index += 1
        
        return self.history[self.cur_history_index]
    
    def history_forward(self):
        if self.cur_history_index <= 0:
            self.cur_history_index = -1
            return ""
        
        self.cur_history_index -= 1
        return self.history[self.cur_history_index]
    
    def key_press_cb(self, buf, event):
        if event.keyval == Gdk.KEY_Return:
            self.process_line()
            return True
        elif event.keyval == Gdk.KEY_Up:
            self.replace_input( self.history_back() )
            return True
        elif event.keyval == Gdk.KEY_Down:
            self.replace_input( self.history_forward() )
            return True
        elif event.string != None:
            insert_mark = self.ui.shell.get_insert()
            select_mark = self.ui.shell.get_selection_bound()
            
            start = self.ui.shell.get_iter_at_mark( self.marks["line_start"] )
            insert = self.ui.shell.get_iter_at_mark( insert_mark )
            select = self.ui.shell.get_iter_at_mark( select_mark )
            
            cmp_start_insert = start.compare( insert )
            
            if start.compare( insert ) == 0 and start.compare( select ) == 0\
            and event.keyval in (Gdk.KEY_BackSpace, Gdk.KEY_Left):
                return True
            
            if start.compare( insert ) <= 0 and start.compare( select ) <= 0:
                return False
            elif start.compare( insert ) > 0 and start.compare( select ) > 0:
                self.ui.shell.place_cursor( start )
            elif insert.compare( select ) < 0:
                self.ui.shell.move_mark( insert_mark, start )
            elif insert.compare( select ) > 0:
                self.ui.shell.move_mark( select_mark, start )
            
        return False
    
    def append_text(self, text, tag):
        insert = self.ui.shell.get_insert()
        end_iter = self.ui.shell.get_end_iter()
        self.ui.shell.move_mark( insert, end_iter )
        self.ui.shell.insert_with_tags_by_name( end_iter,
                                                text,
                                                tag )
        self.ui.shell_view.scroll_to_mark( insert, 0, True, 0, 1 )
