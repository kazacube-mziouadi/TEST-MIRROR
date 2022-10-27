# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import datetime
import os

class xml_import_processing(models.Model):
    _inherit = "xml.import.processing"
    _order = 'mf_is_model desc, id'

    # ===========================================================================
    # FIELDS
    # ===========================================================================
    mf_imported_from_simulation = fields.Boolean(string="Imported from simulation", default=False)
    mf_process_conversion_id = fields.Many2one('mf.xlsx.convert.xml', string='XLSX Conversion', ondelete='set null')
    mf_process_file_to_convert = fields.Binary(string="XLSX/CSV file to convert")
    mf_process_file_to_convert_name = fields.Char()
    mf_conversion_message = fields.Char(string="Conversion information", readonly=True)
    mf_is_model = fields.Boolean(string="Is model", default=False)
        
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
    @api.multi
    def copy(self, default=None):
        """
        Overrider of the copy method
        """
        if not default:
            default = {}
        default['mf_is_model'] = False
        res = super(xml_import_processing, self).copy(default=default)
        return res

    @api.multi
    def unlink(self):
        for xml_import_processing_id in self:
            if xml_import_processing_id.mf_is_model:
                raise ValidationError(_('You cannot delete a processing which is model.\nYou should first unselect them as model or unselect the models.'))

        return super(xml_import_processing, self).unlink()

    @api.onchange("mf_is_model")
    def _onchange_is_model(self):
        if not self.mf_is_model:
            default_config = self.env['mf.modules.config'].search([], None, 1)
            #TODO : réussir a valider la condition, actuellement le self.id retourne un "<openerp.models.NewId object at 0x7f21a13e7d50>"
            if default_config and default_config.default_processing_wizard.id == self.id:
                self.mf_is_model = True
                raise ValidationError(_("This processing is used as default processing.\nIt must stay as model as it is in default configuration")) 

    @api.one
    def mf_xlsx_conversion(self):
        """
        Use xlsx conversion objet for create xlsx file and write file in preprocessing object.
        """ 
        if not self.mf_process_conversion_id:
            return True
        if not self.mf_process_file_to_convert:
            return False
            
        self.mf_process_conversion_id.write({'file_to_convert':self.mf_process_file_to_convert, 
                                                'file_to_convert_name':self.mf_process_file_to_convert_name,
                                                })
        
        conversion_ok = self.mf_process_conversion_id.mf_convert()
        conversion_ok = conversion_ok[0]
        
        self.mf_conversion_message = self.mf_process_conversion_id.execution_message
        if conversion_ok:
            self.write({'file': self.mf_process_conversion_id.xml_file, 
                        'fname': self.mf_process_conversion_id.xml_file_name,
                        })
        return conversion_ok

    @api.multi
    def preprocessing_xml_file(self):
        if self.mf_process_conversion_id:
            # Don't use the current object conversion method, because it also exists in the preprocessing object 
            # Change all preprocessing parameters else the preprocessing will use it's own paramters
            self.preprocessing_id.write({'mf_preprocess_conversion_id':self.mf_process_conversion_id.id, 
                                        'mf_preprocess_file_to_convert':self.mf_process_file_to_convert,
                                        'mf_preprocess_file_to_convert_name':self.mf_process_file_to_convert_name,
                                        'file':False,
                                        'preprocessing_file':False,
                                        })  

        if self.preprocessing_id:                                              
            super(xml_import_processing, self).preprocessing_xml_file()

        # After preprocessing, we get the information from object
        if self.mf_process_conversion_id:
            self.write({
                'file': self.preprocessing_id.file, 
                'fname': self.preprocessing_id.fname,
                'mf_conversion_message': self.preprocessing_id.mf_preprocess_conversion_id.execution_message,
            })

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
        # Dict containing all the records' ids that have already been created, so they don't get created again
        # Ex : { "product.product": [1, 5, 9], "mrp.bom", [1, 5] }
        created_records_dict = {}
        for simulation_line_id in self.processing_simulate_action_ids:
            simulation_line_id.process_data_import(created_records_dict)

    def mf_import_product_document(self, product_code, mpr_bom):
        directory_id = self.model_id.mf_documents_directory_id
        code_product_version_separator = self.model_id.mf_file_separator
        if directory_id.directory_scan_is_needed_mf: directory_id.mf_scan_directory()
        for file_to_import in directory_id.files_mf:
            file_product_code, file_product_version, file_extension = self._mf_get_data_from_file_name(file_to_import.name, product_code, code_product_version_separator)
            if file_product_code == product_code:
                self._mf_import_document_to_product_internal_plans(file_to_import, file_product_code, file_product_version, file_extension, mpr_bom)

    def _mf_import_document_to_product_internal_plans(self, file_to_import, product_code, product_version, file_extension, mpr_bom):
        product_id = self.env["product.product"].search([("code", '=', product_code)], None, 1)
        if not product_id:
            return

        version_id = self.env["product.version.historical"].search([
            ("product_id", '=', product_id.id), 
            ("version", '=', product_version)
        ], None, 1)
            
        root_directory_id = self.env["document.directory"].search([("name", '=', "Root")], None, 1)
        
        existing_document = self.env["document.openprod"].search([
            ("directory_id","=",root_directory_id.id),
            ("name","=",product_code),
            ("version","=",product_version),
            ("extension","=",file_extension)
        ],order="create_date desc",limit=1)

        if existing_document:
            while existing_document.last_version_id:
                existing_document = existing_document.last_version_id

            date_formated = self.env['mf.tools'].mf_convert_from_UTC_to_tz(datetime.now(), self.env.user.tz).strftime("%d-%m-%Y %H:%M:%S")
            if product_version:
                product_version_date = ("%s [%s]") % (product_version,date_formated)
            else:
                product_version_date = ("[%s]") % (product_version,date_formated)

            document = existing_document.create_new_version(product_version_date)
            document.write({"attachment": file_to_import.content_mf})
        else:
            document = self.env["document.openprod"].create({
                "directory_id": root_directory_id.id,
                "name": product_code,
                "version": product_version,
                "extension": file_extension,
                "attachment": file_to_import.content_mf,
                "company_id": self.env.user.company_id.id,
                "user_id": self.env.user.id,
            })

        product_write_dict = {
            "internal_plan_ids": [(4, document.id, 0)]
        }
        if not version_id and product_version:
            product_write_dict["version_historical_ids"] = [(0, 0, {
                "version": product_version,
                "start_date": datetime.datetime.now()
            })]
        product_id.write(product_write_dict)
        if mpr_bom:
            mrp_bom_write_dict = {
                "document_ids": [(4, document.id, 0)]
            }
            mpr_bom.write(mrp_bom_write_dict)

        file_to_import.delete()

    def _mf_get_data_from_file_name(self, file_name, code_product, code_product_version_separator):
        if not code_product_version_separator:
            code_product_version_separator = "-"
        file_extension = self.env["mf.tools"].mf_get_file_name_extension(file_name)
        file_without_extension = self.env["mf.tools"].mf_get_file_name_without_extension(file_name)
        file_name_split_list = file_without_extension.split(code_product_version_separator)

        product_code = False
        product_version = False
        if file_without_extension == code_product:
            product_code = code_product
        elif file_without_extension.startswith(code_product):
            if len(file_name_split_list) > 1:
                product_version = file_name_split_list.pop()
            product_code = code_product_version_separator.join(file_name_split_list)

        return product_code, product_version, file_extension

    @api.multi
    def clear_history(self, history):
        self.processing_simulate_action_ids.unlink()
        super(xml_import_processing, self).clear_history(history)

    @api.multi
    def simulate_file_analyse(self):
        if self.model_id.mf_documents_directory_id:
            self.model_id.mf_documents_directory_id.mf_scan_directory()
        super(xml_import_processing, self).simulate_file_analyse()


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
