# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError, ValidationError
import lxml
import base64
import sys
from datetime import datetime

class xml_import_processing(models.Model):
    _inherit = 'xml.import.processing'

    @api.multi
    def mf_get_file_content(self):
        if self.preprocessing_file:
            lines = base64.b64decode(self.preprocessing_file)
        elif self.file:
            if self.preprocessing_id:
                if self.preprocessing_file:
                    self.write({'preprocessing_file':False})
                self.preprocessing_xml_file()
                lines = base64.b64decode(self.preprocessing_file)
            else:    
                lines = base64.b64decode(self.file)

        return lines

    @api.multi
    def mf_simulate_file_analyse(self,lines,simulation_for_compare = False):
        """
        simulate import au file or preprocessing file and create a list of simualte action. Put processsing in simulate state.
        """
        error = False
        msg = ''
                
        try:
            root = lxml.etree.fromstring(lines)
        except:
            msg = 'Invalid XML file.'
            error = True
        
        if not error:
            configuration_table_rc = self.model_id
            self.env.cr.commit()
            history = []
            configuration_table_rc.with_context(source='simulation').interpreter(root, history_list=history)
            self.create_simulate_import(history)
            if not simulation_for_compare:
                self.wkf_processing_sim()
            
        if error:    
            self.wkf_processing_error()
            self.write({'error_message': msg})
    
    
    @api.multi
    def mf_file_analyse(self,lines):
        """
        Retrieves the file to be analyzed, retrieves its contents as a string.        
        Create the XML object . etree . Element Tree . Element that contains the root of the XML file tree 
        And launches the method to read and create the objects contained in the XML file.
        """
        error = False
        msg = ''
                
        try:
            root = lxml.etree.fromstring(lines)
        except:
            msg = 'Invalid XML file.'
            error = True
        
        if not error:
            configuration_table_rc = self.model_id
            self.env.cr.commit()
            try:
                history = []
                configuration_table_rc.with_context(source='import').interpreter(root, history_list=history)
                self.create_history(history)
                self.wkf_processing_done()
                error = False
            except Exception as e:
                error = ''
                self.env.cr.rollback()
                if e and isinstance(e.args, tuple):
                    for i in e.args:
                        if msg:
                            msg = '%s\n%s\n%s'%(error, i, msg) 
                        else:
                            msg = i
                            
                error = True
            
        if error:    
            self.wkf_processing_error()
            self.write({'error_message': msg})