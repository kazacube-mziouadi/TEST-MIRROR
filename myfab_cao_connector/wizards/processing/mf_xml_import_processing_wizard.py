# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from datetime import datetime

class mf_xml_import_processing_wizard(models.TransientModel):
    """ 
        wizard that create XML and XLSX processing dans launch them
    """
    _name = 'mf.xml.import.processing.wizard'

    name = fields.Char(required=True, readonly=True, default=lambda self: self._mf_name_sequence())
    mf_processing_id = fields.Many2one('xml.import.processing', string="Processing", domain=[('mf_is_model', '=', True)], required=True, default=lambda self: self._mf_compute_default_processing_id())
    mf_stop_at_simulation = fields.Boolean(string='Stop at simulation', default=lambda self: self._mf_compute_default_stop_at_simulation())
    mf_xml_import_processing_wizard_line_ids = fields.One2many('mf.xml.import.processing.wizard.line','mf_process_conversion_id', string='Files')
 
    #TODO : the sequence is incremented at wizard opening and at validation
    # We will resolve this bug later because it's not blocking        

    # ===========================================================================
    # DEFAULT VALUE METHODS
    # ===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(mf_xml_import_processing_wizard, self).default_get(fields_list=fields_list)
        return res

    def _mf_default_configuration(self):
        return self.env['mf.modules.config'].search([], None, 1)

    def _mf_compute_default_processing_id(self):
        mf_config = self._mf_default_configuration()
        if mf_config:
            return mf_config.default_processing_wizard
        return False

    def _mf_compute_default_stop_at_simulation(self):
        mf_config = self._mf_default_configuration()
        if mf_config:
            return mf_config.default_stop_at_simulation
        return False

    def _mf_name_sequence(self):
        now = self.env['mf.tools'].mf_convert_from_UTC_to_tz(datetime.now(), self.env.user.tz).strftime("%d-%m-%Y %H:%M")
        sequence = self.env['ir.sequence'].get('xml.import.processing')
        new_name = ("%s %s") % (sequence, now)
        return new_name

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.one
    def create_and_process(self):
        if self._mf_are_parameters_ok():
            files = []
            file_names_already_present = []
            for file in self.mf_xml_import_processing_wizard_line_ids:
                #TODO : s'assurer que le contenu du fichier est identique. Ne pas se baser que sur le nom
                if file.file_name and file.file_name not in file_names_already_present:
                    file_names_already_present.append(file.file_name)
                    files.append(file)
            self._mf_files_to_process(files)
            return self._mf_open_created_records()

    def _mf_are_parameters_ok(self):
        if self.env['xml.import.processing'].search([("name", '=', self.name)], None, 1):
            raise ValidationError(_("At least one processing with same name already exists. Enter an other name"))
        if not self.mf_processing_id and not self.mf_processing_id.model_id: 
            raise ValidationError(_("Select at least Processing or Configuration table."))
        for file in self.mf_xml_import_processing_wizard_line_ids:
            if file.file_name.split(".")[-1].upper() in ["XLSX","CSV","TXT"] and not self.mf_processing_id.mf_process_conversion_id:
                raise ValidationError(_("Select a XLSX/CSV Conversion."))
        return True

    def _mf_files_to_process(self, files):
        new_processings = []
        for file in files:
            new_processing = self._mf_create_process(file)
            if new_processing:
                new_processings.append(new_processing)
        self._mf_launch_processings(new_processings)

    def _mf_create_process(self, file_id):
        new_file = False
        new_processing = False

        file_extension = file_id.file_name.split(".")[-1].upper()
        if file_extension == "XML":
            new_file = {
                "file":file_id.file,
                "fname":file_id.file_name,
                "mf_process_file_to_convert":False,
                "mf_process_file_to_convert_name":False,
                "mf_process_conversion_id":False,
            }
        elif file_extension in ["XLSX","CSV","TXT"] and self.mf_processing_id.mf_process_conversion_id:
            new_file = {
                "file":False,
                "fname":False,
                "mf_process_file_to_convert":file_id.file,
                "mf_process_file_to_convert_name":file_id.file_name,
                "mf_process_conversion_id":self.mf_processing_id.mf_process_conversion_id.id,
            }
        if new_file and self.mf_processing_id.model_id:
            new_file["name"] = self.name
            new_file["preprocessing_file"] = False
            new_file["prefname"] = False
            new_file["preprocessing_id"] = self.mf_processing_id.preprocessing_id.id
            new_file["model_id"] = self.mf_processing_id.model_id.id
            new_processing = self.env['xml.import.processing'].create(new_file)

        return new_processing

    def _mf_launch_processings(self, new_processings):
        for new_process in new_processings:
            new_process.preprocessing_xml_file()
            new_process.simulate_file_analyse()
            if not self.mf_stop_at_simulation:
                new_process.file_analyse()

    def _mf_open_created_records(self):
        return {
            "view_mode": "tree,form",
            "target": "main",
            "type": "ir.actions.act_window",
            "res_model": "xml.import.processing",
            "domain": [("name","=",self.name)],
        }
