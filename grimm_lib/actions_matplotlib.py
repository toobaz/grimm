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

import os

from gi.repository import Gtk, Pango

import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas

from .config import STUFF_DIR
from .actions import GrimmAction
from .ui import Ui

"""
This is the main module for the definition of StatsModels actions.

Contributed actions, however, can be added through other modules.
"""

class GrimmMatplotlibPlot(GrimmAction):
    def __init__(self, *args):
        super( GrimmMatplotlibPlot, self ).__init__( *args )
        
        self.ui = Ui( 'grimm', os.path.join( STUFF_DIR, 'dialogs', self.glade_file ) )
        
        self.used = set()
        
        self.ui.connect_signals( self )

class Scatter(GrimmMatplotlibPlot):
    name = label = description = "Scatterplot"
    path = "/MenuBar/GraphsMenu"
    grimm_command = "scatter"
    
    glade_file = "scatterplot.glade"
    
    def show_in_in_series(self, store, the_iter, data):
        return self.grimm.ui.series[the_iter][0] not in self.used

    def show_in_dep_series(self, *args):
        return self.grimm.ui.series[the_iter][0] in self.used
    
    def add_indep(self, *args):
        model, rows = self.ui.in_selection.get_selected_rows()
        
        for row in rows:
            name = model[row][0]
            self.used.add( name )
            self.ui.series_indep.append( [name] )
        
        self.in_series.refilter()
    
    def remove_indep(self, *args):
        model, rows = self.ui.dep_selection.get_selected_rows()
        
        # We cannot just delete rows as we go, because when one is deleted, the
        # following ones change index. We store the iters...
        iters = []
        for row in rows:
            iters.append( model.get_iter( row ) )
            name = model[row][0]
        
        # ... and then delete them:
        for an_iter in iters:
            print("remove", an_iter)
            self.ui.series_indep.remove( an_iter )
        
        self.in_series.refilter()
    
    def set_dep(self, *args):
        model, rows = self.ui.in_selection.get_selected_rows()
        
        if len( rows ) != 1:
            # TODO: error dialog
            return
        
        row = rows[0]
        
        name = model[row][0]
        old_name = self.ui.dep.get_text()
        if old_name:
            self.used.remove( old_name )
        self.used.add( name )
        self.ui.dep.set_text( name )
        
        self.in_series.refilter()
    
    def validity_checks(self, *args):
        valid = all( (self.ui.series_indep, self.ui.dep.get_text()) )
        self.ui.OK.set_sensitive( valid )
        return len( self.ui.series_indep ) and self.ui.dep.get_text()
    
    def run(self, *args):
        series = self.grimm.ui.series
        self.in_series = Gtk.TreeModelFilter( child_model=series )
        self.in_series.set_visible_func( self.show_in_in_series, None )
                
        self.ui.series_view.set_model( self.in_series )
        
        resp = self.ui.input_dialog.run()
        if resp != 1:
            return
        self.ui.input_dialog.hide()
        
        endog = self.grimm.df[self.ui.dep.get_text()]
        exog = self.grimm.df[[row[0] for row in self.ui.series_indep]]
        
        args = [endog, exog]
        kwargs = {}
        self.run_inner( *args, **krwargs )
    
    def run_inner(self, endog, exog, **kwargs ):
        
        signs = ['x', '+']
        colours = ['r', 'b']
                
        f = plt.figure()
        
        var_index = 0
        for var in exog.columns:
            sign = signs[var_index % len( signs )]
            colour = colours[var_index % len( colours )]
            plt.plot( endog, exog[var], colour+sign )
            var_index += 1
        
        canvas = FigureCanvas( f )
        
        self.ui.output_vbox.pack_start( canvas, True, True, 0 )
        canvas.show()
        self.ui.output_dialog.run()
        self.ui.output_dialog.hide()

