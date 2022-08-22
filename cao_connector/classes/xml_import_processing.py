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
    mf_documents_directory_id = fields.Many2one("physical.directory.mf", string="Documents directory", ondelete="cascade",
                                                help="Directory from which the documents will be scanned and attached to the imported records")

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
    def create_simulate_import(self, history):
        """
        Create list of simulate action of import.
        """
        self.write({"processing_simulate_action_ids": history})
        root_sim_actions_list = self.processing_simulate_action_ids
        self.set_tree_view_sim_action_children(root_sim_actions_list)

    def set_tree_view_sim_action_children(self, root_sim_actions_list):
        for sim_action_id in self.processing_simulate_action_ids:
            sim_action_id.set_tree_view_sim_action_children(root_sim_actions_list)

    @api.multi
    def file_analyse(self):
        if self.state == "sim":
            self.import_simulation_lines()
            if self.mf_documents_directory_id:
                if self.mf_documents_directory_id.directory_scan_is_needed_mf:
                    self.mf_documents_directory_id.scan_directory()
                self.import_documents_from_directory()
            self.wkf_processing_done()
        else:
            super(xml_import_processing, self).file_analyse()

    def import_simulation_lines(self):
        for simulation_line_id in self.processing_simulate_action_ids:
            simulation_line_id.process_data_import()

    def import_documents_from_directory(self):
        for file_to_import in self.mf_documents_directory_id.files_mf:
            self.import_document_to_product_internal_plans(file_to_import)

    def import_document_to_product_internal_plans(self, file_to_import):
        file_name_extension_split = file_to_import.name.split('.')
        file_name_without_extension = file_name_extension_split[0]
        file_extension = file_name_extension_split[1]
        file_name_split_list = file_name_without_extension.split('-')
        product_code = file_name_split_list[0]
        product_version = file_name_split_list[1]
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
            "search_view_id": self.env.ref("cao_connector.mf_view_tree_xml_import_processing_sim_action").id,
            "res_model": "xml.import.processing.sim.action",
            "type": "ir.actions.act_window",
            "target": "current",
            "domain": "[('processing_id', '=', " + str(self.id) + "),('mf_tree_view_sim_action_parent_id', '=', False)]"
        }