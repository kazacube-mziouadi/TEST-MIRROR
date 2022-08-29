# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import datetime
import os

class xml_import_processing(models.Model):
    _inherit = "xml.import.processing"

    # ===========================================================================
    # FIELDS
    # ===========================================================================
    mf_imported_from_simulation = fields.Boolean(string="Imported from simulation", default=False)
    mf_process_xlsx_conversion_id = fields.Many2one('mf.xlsx.convert.xml', string='XLSX Conversion', ondelete='set null')
    mf_process_xlsx_file = fields.Binary(string="XLSX file to convert")
    mf_process_xlsx_file_name = fields.Char()
    mf_conversion_message = fields.Char(string="Conversion information", readonly=True)
        
    # ===========================================================================
    # METHODS - WORKFLOW
    # ===========================================================================
    @api.multi
    def wkf_processing_wait(self):
        self.write({"mf_imported_from_simulation": False})
        return super(xml_import_processing, self).wkf_processing_wait()

    @api.multi
    def wkf_processing_done(self):
        if self.state == "sim":
            self.write({"state": "done", "error_message": '', "mf_imported_from_simulation": True})
            return True
        else:
            return super(xml_import_processing, self).wkf_processing_done()

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.one
    def mf_xlsx_conversion(self):
        """
        Use xlsx conversion objet for create xlsx file and write file in preprocessing object.
        """ 
        if not self.mf_process_xlsx_conversion_id:
            return True
        if not self.mf_process_xlsx_file:
            return False
            
        self.mf_process_xlsx_conversion_id.write({'xlsx_file':self.mf_process_xlsx_file, 
                                                'xlsx_file_name':self.mf_process_xlsx_file_name,
                                                })
        
        conversion_ok = self.mf_process_xlsx_conversion_id.mf_convert()
        conversion_ok = conversion_ok[0]
        
        self.mf_conversion_message = self.mf_process_xlsx_conversion_id.execution_message
        if conversion_ok:
            self.write({'file': self.mf_process_xlsx_conversion_id.xml_file, 
                        'fname': self.mf_process_xlsx_conversion_id.xml_file_name,
                        })
        return conversion_ok

    @api.multi
    def preprocessing_xml_file(self):
        if self.mf_process_xlsx_conversion_id:
            # Don't use the current object conversion method, because it also exists in the preprocessing object 
            # Change all preprocessing parameters else the preprocessing will use it's own paramters
            self.preprocessing_id.write({'mf_preprocess_xlsx_conversion_id':self.mf_process_xlsx_conversion_id.id, 
                                        'mf_preprocess_xlsx_file':self.mf_process_xlsx_file,
                                        'mf_preprocess_xlsx_file_name':self.mf_process_xlsx_file_name,
                                        'file':False,
                                        'preprocessing_file':False,
                                        })  
                                                      
        super(xml_import_processing, self).preprocessing_xml_file()

        # After preprocessing, we get the information from object
        if self.mf_process_xlsx_conversion_id:
            self.mf_conversion_message = self.preprocessing_id.mf_preprocess_xlsx_conversion_id.execution_message

    def create_simulate_import(self, history):
        """
        Create list of simulate action of import.
        """
        self.write({"processing_simulate_action_ids": history})
        self.set_tree_view_sim_action_children()

    def set_tree_view_sim_action_children(self):
        for sim_action_id in self.processing_simulate_action_ids:
            sim_action_id.set_tree_view_sim_action_children()

    @api.multi
    def file_analyse(self):
        if self.state == "sim":
            self.import_simulation_lines()
            self.wkf_processing_done()
        else:
            super(xml_import_processing, self).file_analyse()

    def import_simulation_lines(self):
        for simulation_line_id in self.processing_simulate_action_ids:
            simulation_line_id.process_data_import()

    def mf_import_product_document(self, product_code):
        directory_id = self.model_id.mf_documents_directory_id
        if directory_id.directory_scan_is_needed_mf:
            directory_id.scan_directory()
        for file_to_import in directory_id.files_mf:
            file_product_code, file_product_version, file_extension = self.mf_get_data_from_file_name(file_to_import.name)
            if file_product_code == product_code:
                self.mf_import_document_to_product_internal_plans(
                    file_to_import, file_product_code, file_product_version, file_extension
                )

    def mf_import_document_to_product_internal_plans(self, file_to_import, product_code, product_version, file_extension):
        product_id = self.env["product.product"].search([("code", '=', product_code)], None, 1)
        if not product_id:
            return
        version_id = self.env["product.version.historical"].search([
            ("product_id", '=', product_id.id), ("version", '=', product_version)
        ], None, 1)
        root_directory_id = self.env["document.directory"].search([("name", '=', "Root")], None, 1)
        product_write_dict = {
            "internal_plan_ids": [(0, 0, {
                "name": product_code,
                "attachment": file_to_import.content_mf,
                "user_id": self.env.user.id,
                "company_id": self.env.user.company_id.id,
                "version": product_version,
                "directory_id": root_directory_id.id,
                "extension": file_extension
            })]
        }
        if not version_id:
            product_write_dict["version_historical_ids"] = [(0, 0, {
                "version": product_version,
                "start_date": datetime.datetime.now()
            })]
        product_id.write(product_write_dict)
        file_to_import.delete()

    @staticmethod
    def mf_get_data_from_file_name(file_name):
        file_name_extension_split = file_name.split('.')
        file_name_without_extension = file_name_extension_split[0]
        file_extension = file_name_extension_split[1]
        file_name_split_list = file_name_without_extension.split('-')
        product_code = file_name_split_list[0]
        product_version = file_name_split_list[1]
        return product_code, product_version, file_extension

    @api.multi
    def clear_history(self, history):
        self.processing_simulate_action_ids.unlink()
        super(xml_import_processing, self).clear_history(history)

    @api.multi
    def analyse_simulation(self):
        return {
            "name": _("Analyse simulation"),
            "view_type": "tree",
            "view_mode": "tree",
            "search_view_id": self.env.ref("myfab_cao_connector.mf_view_tree_xml_import_processing_sim_action").id,
            "res_model": "xml.import.processing.sim.action",
            "type": "ir.actions.act_window",
            "target": "current",
            "domain": "[('processing_id', '=', " + str(self.id) + "),('mf_tree_view_sim_action_parent_id', '=', False)]"
        }