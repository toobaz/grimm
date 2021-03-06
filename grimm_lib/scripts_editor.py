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
from io import StringIO
import sys
import traceback
import code
import os

from .actions import GrimmAction

# Constants describing the changed status (compared to the saved copy) of a
# script:
UNCHANGED, CHANGED, OPENING = range( 3 )

class Script(Gtk.ScrolledWindow):
    uri = ''
    lm = GtkSource.LanguageManager.get_default()
    lang = lm.get_language( "python" )
    
    def __init__(self, ui, uri=None, name=None):
        Gtk.ScrolledWindow.__init__( self )
        
        self.ui = ui
        
        self.buffer = GtkSource.Buffer()
        self.buffer.set_language( self.lang )
        
        self.view = GtkSource.View( buffer=self.buffer )
        self.view.set_insert_spaces_instead_of_tabs( True )
        self.view.set_indent_width( 4 )
        self.view.set_auto_indent( True )
        fontdesc = Pango.FontDescription( "monospace" )
        self.view.modify_font( fontdesc )
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
            self.status = OPENING
        else:
            self.file = None
            self.status = UNCHANGED
        
        self.buffer.connect( "changed", self.changed )
        
        self.name = name
        
        self.build_label()
        self.show_all()
    
    def build_label(self):
        self.name_label = Gtk.Label( self.name )
        self.label = Gtk.Box()
        self.label.pack_start( self.name_label, False, False, 0 )
        # From http://www.micahcarrick.com/gtk-notebook-tabs-with-close-button.html
        button = Gtk.Button()
        button.add( Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU) )
        button.connect( "clicked", self.close )
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click( False )
        provider = Gtk.CssProvider()
        provider.load_from_path("stuff/button_style.txt")
        # 600 = GTK_STYLE_PROVIDER_PRIORITY_APPLICATION
        button.get_style_context().add_provider(provider, 600) 
        self.label.pack_start( button, False, False, 0 )
        self.label.show_all()
    
    def close(self, *args):
        if self.status == CHANGED:
            text = "Do you want to save changes to script «%s» before closing?" % self.name
            dialog = Gtk.MessageDialog( self.ui.main_win,
                                        Gtk.DialogFlags.MODAL,
                                        Gtk.MessageType.WARNING,
                                        text="Unsaved changes",
                                        secondary_text=text )
            
            dialog.add_buttons( Gtk.STOCK_CANCEL,
                                Gtk.ResponseType.CANCEL,
                                "Close without saving",
                                Gtk.ResponseType.REJECT,
                                Gtk.STOCK_SAVE,
                                Gtk.ResponseType.ACCEPT )
            
            resp = dialog.run()
            dialog.hide()
            
            if resp in (Gtk.ResponseType.CANCEL,
                        Gtk.ResponseType.DELETE_EVENT):
                return
            
            if resp == Gtk.ResponseType.ACCEPT:
                self.save()
                # If "save" calls "save_as" which is then canceled, the document
                # could still be unsaved:
                if self.status == CHANGED:
                    return
        
        self.destroy()
    
    def change_uri(self, uri):
        self.file = Gio.File.new_for_uri( uri )
        name = self.file.get_basename()
        self.name_label.set_text( name )
    
    def save(self):
        if not self.file:
            return self.save_as()
        
        path = self.file.get_path()
        fout = open( path, 'w' )
        fout.write( self.text() )
        fout.close()
        self.status = UNCHANGED
        self.name_label.set_text( self.name )
    
    def save_as(self):
        resp = self.ui.script_filesaver.run()
        self.ui.script_filesaver.hide()
        if resp == Gtk.ResponseType.OK:
            new_uri = self.ui.script_filesaver.get_uri()
            self.change_uri( new_uri )
            self.save()
    
    def text(self):
        start, end = self.buffer.get_bounds()
        text = self.buffer.get_text( start, end, False )
        return text
    
    def changed(self, *args):
        if self.status == OPENING:
            self.status = UNCHANGED
            
        elif self.status == UNCHANGED:
            self.status = CHANGED
            self.name_label.set_text( "*%s" % self.name )

class GrimmScriptsEditor(Gtk.Box):
    def __init__(self, grimm_instance):
        Gtk.Box.__init__( self )
        
        self.opened_scripts = set()
        self.ui = grimm_instance.ui
        self.locals = grimm_instance.context
        self.shell = grimm_instance.python_shell
        self.ui_manager = grimm_instance.ui_manager
        
        self.set_orientation( Gtk.Orientation.VERTICAL )
        
        scripts_bar = self.build_toolbar()
        
        self.pack_start( scripts_bar, False, False, 0 )
        self.pack_start( self.ui.scripts_book, True, True, 0 )
        
        self.script_new()
        
    def build_toolbar(self):
        
        actions = GrimmScriptAction.register()
                
        for action in actions:
            action.scripts_merge_id = self.ui_manager.new_merge_id()
            
            self.ui_manager.add_ui( action.scripts_merge_id,
                                    "/ScriptsToolbar",
                                    action.name,
                                    action.name,
                                    Gtk.UIManagerItemType.AUTO,
                                    False )
        
        return self.ui_manager.get_widget( "/ScriptsToolbar" )
    
    def script_new(self, *args):
        i = 0
        while True:
            label = "Unsaved script %d" % i
            if label not in [s.name for s in self.ui.scripts_book.get_children()]:
                break
            i += 1
        
        script = Script( self.ui, name=label )
        
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
            
            script = Script( self.ui, uri=self.ui.script_fileopener.get_uri() )
            self.ui.scripts_book.append_page( script, script.label )
            index = self.ui.scripts_book.page_num( script.view )
            self.ui.scripts_book.set_current_page( index )
    
    def script_save(self, *args):
        active_index = self.ui.scripts_book.get_current_page()
        active_script = self.ui.scripts_book.get_nth_page( active_index )
        active_script.save()
    
    def script_save_as(self, *args):
        active_index = self.ui.scripts_book.get_current_page()
        active_script = self.ui.scripts_book.get_nth_page( active_index )
        active_script.save_as()
    
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
        active_script.close()
    
    def script_undo(self, *args):
        active_index = self.ui.scripts_book.get_current_page()
        active_script = self.ui.scripts_book.get_nth_page( active_index )
        if active_script.buffer.can_undo():
            active_script.buffer.undo()
    
    def script_redo(self, *args):
        active_index = self.ui.scripts_book.get_current_page()
        active_script = self.ui.scripts_book.get_nth_page( active_index )
        active_script.buffer.redo()
        if active_script.buffer.can_redo():
            active_script.buffer.redo()

class GrimmScriptAction(GrimmAction):
    path = "/MenuBar/ScriptsMenu"
    
    def run(self, *args):
        meth = getattr( self.grimm.scripts_editor, "script_%s" % self.method )
        meth()

class GrimmScriptNew(GrimmScriptAction):
    name = label = description = "New"
    icon = Gtk.STOCK_NEW
    accel = "<Control>n"
    method = "new"

class GrimmScriptOpen(GrimmScriptAction):
    name = label = description = "Open"
    icon = Gtk.STOCK_OPEN
    accel = "<Control><Shift>o"
    method = "open"

class GrimmScriptSave(GrimmScriptAction):
    name = label = description = "Save"
    icon = Gtk.STOCK_SAVE
    accel = "<Control>s"
    method = "save"

class GrimmScriptSaveAs(GrimmScriptAction):
    name = label = description = "Save as..."
    icon = Gtk.STOCK_SAVE_AS
    accel = "<Control><Shift>s"
    method = "save_as"

class GrimmScriptRun(GrimmScriptAction):
    name = label = description = "Run"
    icon = Gtk.STOCK_EXECUTE
    accel = "<Control>r"
    method = "run"

class GrimmScriptUndo(GrimmScriptAction):
    name = label = description = "Undo"
    icon = Gtk.STOCK_UNDO
    accel = "<Control>z"
    method = "undo"

class GrimmScriptRedo(GrimmScriptAction):
    name = label = description = "Redo"
    icon = Gtk.STOCK_REDO
    accel = "<Control>y"
    method = "redo"

class GrimmScriptClose(GrimmScriptAction):
    name = label = description = "Close"
    icon = Gtk.STOCK_CLOSE
    accel = "<Control>w"
    method = "close"
