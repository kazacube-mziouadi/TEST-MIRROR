# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules
from datetime import datetime
from openerp.exceptions import ValidationError
import pytz
from ftplib import FTP
import pysftp

class MFTools(models.Model):
    _name = "mf.tools"

    ####################################################################
    # DATE & TIME conversion tools
    ####################################################################
    def mf_convert_from_tz_to_UTC(self, date_in, t_from, date_in_format = '%Y-%m-%d %H:%M:%S'):
        return self.mf_convert_tz(date_in, t_from, 'UTC', date_in_format)

    def mf_convert_from_UTC_to_tz(self, date_in, t_to, date_in_format = '%Y-%m-%d %H:%M:%S'):
        return self.mf_convert_tz(date_in, 'UTC', t_to, date_in_format)

    def mf_get_time_str_from_time_float(self, time_float):
        return self.mf_get_hours_str_from_time_float(time_float) + ':' + self.mf_get_minutes_str_from_time_float(time_float)

    @staticmethod
    def mf_convert_tz(date_in, t_from, t_to, date_in_format ='%Y-%m-%d %H:%M:%S'):
        if type(date_in) != datetime:
            date_in = datetime.strptime(date_in, date_in_format)
        tz_from = pytz.timezone(t_from)
        date_without_tz = tz_from.localize(date_in)
        tz_to = pytz.timezone(t_to)
        date_out = date_without_tz.astimezone(tz_to)
        return (date_out)

    @staticmethod
    def mf_get_hours_str_from_time_float(time_float):
        # Get integer part of float
        default_end_time_integer_part_float = time_float // 1
        return str(int(default_end_time_integer_part_float))

    @staticmethod
    def mf_get_minutes_str_from_time_float(time_float):
        # Get decimal part of float
        default_end_time_decimal_part_float = time_float % 1
        return str(int(round(60 * default_end_time_decimal_part_float)))

    ####################################################################
    # Dynamic execution tools
    ####################################################################
    """
       Launch a method at format (for example) "method_name(paramInt, 'paramString')" on a list of records.
       It's not a static method as "self" is used through the exec() method
    """
    def mf_launch_method_on_records(self, method_name, record_ids):
        record_ids_str_ids_list = [str(record_id.id) for record_id in record_ids]
        exec("self.env['" + record_ids[0]._name + "'].search([('id', 'in', " + str(record_ids_str_ids_list) + ")])." + method_name)

    ####################################################################
    # Fields tools
    ####################################################################
    """
        For a given many2one ir.model.field, returns the reverse field one2many field
    """
    def mf_get_reverse_field_id(self, field_id):
        model_id = self.env["ir.model"].search([("model", '=', field_id.relation)])
        if field_id.relation_field:
            # relation_field is only the string name of the reverse relation field ; we have to return the field record
            return self.env["ir.model.fields"].search([("model_id", '=', model_id.id), ("name", '=', field_id.relation_field)])
        else:
            return self.env["ir.model.fields"].search([
                ("model_id", '=', model_id.id), ("relation", '=', field_id.model_id.model), ("relation_field", '=', field_id.name)
            ])

    ####################################################################
    # Comparison tools
    ####################################################################
    """
        Compare 2 lists : return True if equals, else False
    """
    @staticmethod
    def are_lists_equal(list1, list2):
        list1.sort()
        list2.sort()
        return list1 == list2

    """
        Compare 2 values, with the second one casted to the type of the first.
        Return True if equals, else False.
    """
    @staticmethod
    def are_values_equal_in_same_type(value_with_master_type, value_to_compare_with):
        if (value_to_compare_with and (value_with_master_type is False or value_with_master_type is None)) or (
            value_with_master_type and (value_to_compare_with is False or value_to_compare_with is None)
        ):
            return False
        return value_with_master_type == type(value_with_master_type)(value_to_compare_with)

    ####################################################################
    # Dict tools
    ####################################################################
    @staticmethod
    def merge_two_dicts(dict_1, dict_2):
        merged_dict = dict_1.copy()   # copies keys and values of x
        merged_dict.update(dict_2)    # modifies z with keys and values of y
        return merged_dict

    def dicts_non_common_elements(self, dict_1, dict_2):
        new_dict = {}
        if type(dict_1) == dict and type(dict_1) == type(dict_2):
            new_dict.update(self.extract_diff_from_element_1(dict_1,dict_2))
            new_dict.update(self.extract_diff_from_element_1(dict_2,dict_1))
        return new_dict

    def extract_diff_from_element_1(self, element_1, element_2):
        new_values = False
        
        if type(element_1) in [dict,list] and type(element_1) == type(element_2):
            if type(element_1) == dict : new_values = {}
            if type(element_1) == list : new_values = []
            # Compare each element from list between element 1 and 2
            for key_1 in element_1:
                values_1 = element_1.get(key_1) if type(element_1) is dict else key_1
                if key_1 in element_2:
                    if type(element_1) == dict:
                        values_2 = element_2.get(key_1) if type(element_2) is dict else key_1
                        new_value_nested = self.extract_diff_from_element_1(values_1,values_2)
                        if new_value_nested:
                            self.add_value_to_dict(new_values, key_1, new_value_nested)
                    else:
                        new_values = False                    
                elif type(element_1) == dict:
                    self.add_value_to_dict(new_values, key_1, values_1)
                else:
                    new_values = values_1
        elif element_1 != element_2:
            new_values = element_1
        
        return new_values

    @staticmethod
    def add_value_to_dict(dict, key, value):
        if key in dict:
            dict[key].append(value)
        else:
            dict[key] = [value]

    @staticmethod
    def generate_reference(model_name, record_id):
        return model_name + ',' + str(record_id)

    ####################################################################
    # File tools
    ####################################################################
    @staticmethod
    def mf_get_file_name_extension(file_name):
        file_extension = file_name.split('.')[-1].upper()
        return file_extension

    @staticmethod
    def mf_get_file_name_without_extension(file_name):
        file_name_split = file_name.split('.')
        file_name_split.pop()
        file_name_without_extension = '.'.join(file_name_split)
        return file_name_without_extension

    ####################################################################
    # FTP tools
    ####################################################################
    @staticmethod
    def mf_login_to_ftp(ftp_adress,login,password):
        ftp = FTP(ftp_adress, login, password)
        ftp.login()
        return ftp

    @staticmethod
    def mf_ftp_move_to_folder(ftp,folder):
        ftp.cwd(folder)  

    @staticmethod
    def mf_send_file_to_ftp(ftp,file):
        ftp.storbinary('STOR ' + file, file)

    @staticmethod
    def mf_quit_ftp(ftp):
        ftp.quit()
    
    ####################################################################
    # SFTP tools
    ####################################################################
    @staticmethod
    def mf_login_to_sftp(sftp_adress,login,password):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(sftp_adress, username=login, password=password, cnopts=cnopts)
        return sftp

    @staticmethod
    def mf_sftp_move_to_folder(sftp,folder):
        if not sftp.exists(folder):
            raise ValidationError(_('The folder provided does not exists on the ftp server'))
        sftp.cwd(folder)  

    @staticmethod
    def mf_send_file_to_sftp(sftp,file):
        sftp.put(file)

    ####################################################################
    # jasper report tools
    ####################################################################

    @staticmethod
    def mf_print_report(self,report,record):
        ctx = self.env.context.copy()            
        report_to_print_id = report.read(['report_id'], load='_classic_write')[0]['report_id']
        if report_to_print_id:
            report_data = self.env['ir.actions.report.xml'].browse(
                report_to_print_id).read(['model', 'report_name'])[0]
            datas = {'ids': record.id, 'model': report_data['model']}
            if ctx and 'jasper' in ctx:
                datas['jasper'] = ctx['jasper']
            (report_file, report_format), model_report = report.render_report(
                self.env.cr, 1, [record.id], report_data['report_name'],
                datas, context=ctx), report_data['report_name']
        return report_file, report_format, model_report