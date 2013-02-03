# -*- coding: utf-8 -*-

import os

from gi.repository import Gtk, Pango

from statsmodels import api as sm

from config import STUFF_DIR
from actions import GrimmAction
from ui import Ui

"""
This is the main module for the definition of StatsModels actions.

Contributed actions, however, can be added through other modules.
"""

class GrimmStatsModelsModel(GrimmAction):
    def __init__(self, *args):
        super( GrimmStatsModelsModel, self ).__init__( *args )
        
        self.ui = Ui( 'grimm', os.path.join( STUFF_DIR, 'dialogs', self.glade_file ) )
        
        self.used = set()
        
        self.ui.connect_signals( self )

class OLS(GrimmStatsModelsModel):
    method = sm.OLS
    name = label = description = "OLS"
    path = "/MenuBar/ModelsMenu"
    
    glade_file = "ols.glade"
    
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
            print "remove", an_iter
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
        kwargs = { "missing"  : "drop",
                   "hasconst" : self.ui.hasconst.get_active() }
        
        reg = self.method( *args, **kwargs ).fit()
        
        summary = reg.summary()
        
        fontdesc = Pango.FontDescription( "monospace" )
        self.ui.outputview.modify_font( fontdesc )
        
        self.ui.output.set_text( str( summary ) )
        resp = self.ui.output_dialog.run()
        self.ui.output_dialog.hide()
    

