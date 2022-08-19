# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError

import base64
from StringIO import StringIO

from openpyxl import load_workbook
from openpyxl.workbook import Workbook

import xml
import xml.etree.ElementTree as ET

class mf_xlsx_convert_to_xml(models.Model):
    _name = 'mf.xlsx.convert.xml'
        
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(required=True)
    configuration_id = fields.Many2one('mf.xlsx.configuration', string='Configuration', ondelete='restrict')
    xlsx_file = fields.Binary()
    xlsx_file_name =  fields.Char()
    xml_file = fields.Binary(readonly=True)
    xml_file_name = fields.Char()
    execution_message = fields.Char(readonly=True)
     
    @api.one
    def mf_convert(self):
        if self._is_parameters_valide():
            self.execution_message = self._mf_convert_to_xml(self.xlsx_file,self.configuration_id)

    def _is_parameters_valide(self):
        if not self.xlsx_file:
            raise ValidationError(_('No Excel file to convert.'))
        
        if not self.configuration_id:
            raise ValidationError(_('Choose a configuration.'))

        return True

    def _mf_convert_to_xml(self, xlsx_file, configuration_id):
        conversion_message = 'Conversion OK'
        xml_file = ''

        xlsx_document = load_workbook(filename=StringIO(base64.decodestring(xlsx_file)), data_only=True)
        if not xlsx_document:
            conversion_message = 'Error loading Excel file'
        else:
            ET_root = ET.Element(configuration_id.root_beacon)
            for sheet_rc in configuration_id.sheet_ids:
                self._mf_convert_sheet_to_xml(ET_root,xlsx_document,sheet_rc)

        print(ET.dump(ET_root))
        raise "end"

        if xml_file:
            ET_root.write(xml_file, encoding="us-ascii", xml_declaration=None, default_namespace=None, method="xml")            

        return (conversion_message,xml_file)

    def _mf_convert_sheet_to_xml(self, ET_root, xlsx_document, sheet_rc):
        ending_line = 0
        xlsx_sheet = xlsx_document[sheet_rc.sheet_name]
        if xlsx_sheet:
            ET_sheet = ET_root
            if sheet_rc.beacon_for_sheet != '': ET_sheet = self._mf_add_last_sub_element(ET_root, sheet_rc.beacon_for_sheet)

            if sheet_rc.ending_line:
                ending_line = sheet_rc.ending_line
            else:
                ending_line = xlsx_sheet.max_row

            xlsx_rows = []
            for xlsx_row in range(sheet_rc.starting_line, ending_line +1):
                xlsx_rows.append(xlsx_row)
            
            row_line = 0
            self._mf_convert_row_to_xml(ET_sheet, xlsx_sheet, xlsx_row, sheet_rc.beacon_per_row, sheet_rc.field_ids, sheet_rc.level_field_id, sheet_rc.field_ids)
    
    def _mf_convert_row_to_xml(self, ET_sheet, xlsx_sheet, xlsx_row, row_beacon, field_rcs, level_rc):
        
        ET_level = self._mf_set_level(ET_sheet, xlsx_sheet, xlsx_row, level_rc)
        
        ET_row = self._mf_add_last_sub_element(ET_level, row_beacon)
        for field_rc in field_rcs:
            
            if field_rc.writing_mode == 'column_value':
                cell_value = self._mf_get_cell_value(xlsx_sheet,xlsx_row,field_rc.column)
            elif field_rc.writing_mode == 'constant_value' and field_rc.fixed_value:
                cell_value = field_rc.fixed_value
            else: 
                cell_value = False

            if cell_value:
                ET_field = self._mf_add_last_sub_element(ET_row, field_rc.beacon, False)
                Old_Value = ''
                if field_rc.attribute:
                    if field_rc.is_merge: Old_Value = ET_field.get(field_rc.attribute, '')
                    ET_field.set(field_rc.attribute, Old_Value + cell_value)
                else:
                    if field_rc.is_merge: Old_Value = ET_field.text
                    ET_field.text = Old_Value + cell_value

    def _mf_set_level(self, ET_sheet, xlsx_sheet, xlsx_row, level_rc):
        
        ET_level = ET_sheet

        if level_rc:
            level_value = self._mf_get_cell_value(xlsx_sheet,xlsx_row,level_rc.column)

            if level_rc.is_numerical_level:
                if level_value != '0':
                    self._mf_add_last_sub_element(ET_level, level_rc.beacon_per_level, False)
            else:
                parent_value = self._mf_get_cell_value(xlsx_sheet,xlsx_row,level_rc.parent_reference_column)
                if parent_value:
                    self._mf_add_last_sub_element(ET_level, level_rc.beacon_per_level, False)
                    
        return ET_level

    def _mf_add_last_sub_element(self, ET_root, beacon_str, add_duplicate_last_beacon = True):
        beacon_list = beacon_str.split('/')

        ET_Temp = ET_root
        cpt = 0
        for beacon in beacon_list:
            cpt +=1
            is_beacon_present = False
            if add_duplicate_last_beacon == False or cpt < len(beacon_list):
                for child in ET_root:
                    if child.tag == beacon : 
                        is_beacon_present = True
                        ET_Temp = child
            if is_beacon_present == False:
                ET_Temp = ET.SubElement(ET_root, beacon)
            ET_root = ET_Temp

        return ET_root

    def _mf_get_cell_value(self, xlsx_sheet, xlsx_row, column):
        cell_value = xlsx_sheet['%s%s'%(column, xlsx_row)].value
        if cell_value == None: return False
    
        #Convert value readed in cell to be used by the rest of the functions
        try:
            if ',' in cell_value:
                cell_value = float(cell_value)
            else:
                cell_value = int(cell_value)
        except:
                cell_value = unicode(cell_value)

        if cell_value == '': return False
        return cell_value

