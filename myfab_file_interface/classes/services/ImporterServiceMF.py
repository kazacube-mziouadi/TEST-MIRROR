from openerp import models, fields, api, _
from openerp.exceptions import MissingError
import logging

logger = logging.getLogger(__name__)
COMMIT_BATCH_QUANTITY = 1000


class ImporterServiceMF(models.TransientModel):
    _name = "importer.service.mf"
    _description = "Importer service myfab"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def import_records_list(self, records_to_process_list):
        records_processed_counter = 0
        for record_to_process_dict in records_to_process_list:
            # try:
                records_returned, status = self.apply_orm_method_to_model(
                    record_to_process_dict["model"],
                    record_to_process_dict["fields"],
                    record_to_process_dict["write"] if "write" in record_to_process_dict else False,
                    record_to_process_dict["method"]
                )
                if "callback" in record_to_process_dict:
                    if record_to_process_dict["method"] == "delete":
                        raise ValueError("A callback method can not be called on a deleted record.")
                    self.env["mf.tools"].mf_launch_method_on_records(record_to_process_dict["callback"], records_returned)
                record_to_process_dict["status"] = status
                records_processed_counter += 1
                # Committing if we reach COMMIT_BATCH_QUANTITY limit since last commit
                if records_processed_counter % COMMIT_BATCH_QUANTITY == 0:
                    logger.info("Committing " + str(COMMIT_BATCH_QUANTITY) + " records")
                    self.env.cr.commit()
                    # Getting the list of the last records processed since last commit
                    records_processed_since_last_commit_list = records_to_process_list[
                        records_processed_counter-COMMIT_BATCH_QUANTITY:records_processed_counter
                    ]
                    for record_processed_dict in records_processed_since_last_commit_list:
                        record_processed_dict["committed"] = True
                    records_processed_counter = 0
            # except Exception as e:
            #     raise Exception(e, record_to_process_dict)
        if records_processed_counter < COMMIT_BATCH_QUANTITY:
            for record_processed_dict in records_to_process_list:
                record_processed_dict["committed"] = True

    # Apply an ORM method (create/write/search/unlink) on the given model_name, with the given dicts :
    #     - record_fields for the fields of the record we are looking for
    #     - record_fields_to_write for the fields we want to update for the searched record (write method only)
    def apply_orm_method_to_model(self, model_name, record_fields_dict, record_to_write_fields_dict, orm_method_name):
        # Retrieving the ID of each relational field recursively
        self.set_relation_fields_to_ids_in_dict(model_name, record_fields_dict)
        if record_to_write_fields_dict:
            self.set_relation_fields_to_ids_in_dict(model_name, record_to_write_fields_dict)
        records_found = self.search_records_by_fields_dict(model_name, record_fields_dict)
        if orm_method_name == "create" or (orm_method_name == "merge" and not records_found):
            if records_found:
                return records_found, "ignored"
            record_created = self.env[model_name].create(
                record_fields_dict if orm_method_name == "create" else record_to_write_fields_dict
            )
            # Odoo CSV id string link creation
            if "id" in record_fields_dict:
                ir_model_data_values = record_fields_dict["id"].split('.')
                self.env["ir.model.data"].create({
                    "module": ir_model_data_values[0],
                    "name": ir_model_data_values[1],
                    "model": model_name,
                    "res_id": record_created.id
                })
            return record_created, "success"
        elif orm_method_name in ["search", "write", "delete", "merge"]:
            if not records_found and orm_method_name != "merge":
                raise MissingError("No record found for model " + model_name + " with fields " + str(record_fields_dict))
            for record_found in records_found:
                if orm_method_name in ["write", "merge"]:
                    record_found.write(record_to_write_fields_dict)
                elif orm_method_name == "delete":
                    record_found.unlink()
            return records_found, "success"
        raise ValueError("The " + orm_method_name + " method is not supported.")

    # Set all the relation fields in the dict to the id of the matching record.
    # If this record doesn't exist, the record is created.
    def set_relation_fields_to_ids_in_dict(self, record_model_name, record_fields_dict):
        for field_name in record_fields_dict:
            if type(record_fields_dict[field_name]) is dict:
                if not record_fields_dict[field_name]:
                    continue
                # Many2one case : we get the id of the related record
                relation_field_id = self.set_relation_field_to_id_in_dict(
                    record_model_name,
                    field_name,
                    record_fields_dict[field_name]
                )
                if relation_field_id:
                    record_fields_dict[field_name] = relation_field_id
            elif type(record_fields_dict[field_name]) is list:
                # Many2many and One2many case : we get the list of ids of the related records
                list_of_one2many_ids = []
                is_list_of_many2one = False
                for one2many_member in record_fields_dict[field_name]:
                    relation_field_id = self.set_relation_field_to_id_in_dict(
                        record_model_name,
                        field_name,
                        one2many_member
                    )
                    if type(relation_field_id) is list:
                        # Odoo many2many ids string
                        list_of_one2many_ids = list_of_one2many_ids + relation_field_id
                    else:
                        list_of_one2many_ids.append(relation_field_id)
                if not is_list_of_many2one:
                    record_fields_dict[field_name] = list_of_one2many_ids
            # Getting booleans out of strings (else it may block at create)
            elif record_fields_dict[field_name] == "True":
                record_fields_dict[field_name] = True
            elif record_fields_dict[field_name] == "False" and record_model_name != "xml.preprocessing.table.rule":
                record_fields_dict[field_name] = False

    """
        Returns the id(s) of the record corresponding to the given relation field(s) dictionary.
        If no id is found the record is created (and it's id returned). 
        If the relation field is a many2one, the id only is returned. 
        Else it returns the tuple permitting it's linking or it's creation during the root record creation.
        https://www.odoo.com/documentation/11.0/reference/orm.html#odoo.models.Model.write
    """
    def set_relation_field_to_id_in_dict(self, parent_model_name, field_name, relation_field_dict):
        # Odoo many2many multi id string processing
        if "id" in relation_field_dict and type(relation_field_dict["id"]) is not int and ',' in relation_field_dict["id"]:
            many2many_id_strings = relation_field_dict["id"].split(',')
            records_ids = []
            for many2many_id_string in many2many_id_strings:
                records_ids.append(self.get_record_id_by_id_string(many2many_id_string))
            # Link to existing records list
            return (6, 0, records_ids)
        if not parent_model_name:
            return False
        parent_model = self.env["ir.model"].search([
            ("model", '=', parent_model_name)
        ], None, 1)
        field_model = self.env["ir.model.fields"].search([
            ("name", '=', field_name),
            ("model_id", '=', parent_model.id)
        ], None, 1)
        # Odoo many2one or many2many alone id string processing
        if "id" in relation_field_dict and type(relation_field_dict["id"]) is not int:
            relation_field_id = self.get_record_id_by_id_string(relation_field_dict["id"])
            # Link to the existing relation record
            return (4, relation_field_id) if field_model.ttype == "many2many" else relation_field_id
        self.set_relation_fields_to_ids_in_dict(field_model.relation, relation_field_dict)
        relation_field_record = self.search_records_by_fields_dict(field_model.relation, relation_field_dict, 1)
        if field_model.ttype == "one2many" and relation_field_record:
            # If a record exists for this one2many element AND is already linked to a many2one, we create a new one.
            # Else, the existing record is linked to our one2many.
            return (0, 0, relation_field_dict) if getattr(
                relation_field_record, field_model.relation_field
            ) else (4, relation_field_record.id)
        elif relation_field_record:
            # Link to the existing relation record
            return relation_field_record.id if field_model.ttype == "many2one" else (4, relation_field_record.id)
        else:
            # Creation of the relation record
            if field_model.ttype == "many2one":
                many2one_created = self.env[field_model.relation].create(relation_field_dict)
                return many2one_created.id
            else:
                return (0, 0, relation_field_dict)

    def search_records_by_fields_dict(self, model_name, record_fields_dict, limit=None):
        record_fields_tuples_list = []
        for field_name, field_value in record_fields_dict.items():
            # Odoo's string id and record(s) not created yet like (0, 0, {'name': 'example'}) are ignored in search
            if (field_name == "id" and not field_value.isdecimal()) or type(field_value) is tuple or (
                type(field_value) is list and len(field_value) > 0 and type(field_value[0]) is tuple
            ):
                continue
            if type(field_value) is list and len(field_value) > 0 and type(field_value[0]) is not tuple:
                # List case
                record_fields_tuples_list.append((field_name, "in", field_value))
            elif type(field_value) is dict and not field_value:
                # Empty dict case
                record_fields_tuples_list.append((field_name, '=', False))
            elif type(field_value) not in [list, tuple]:
                # Other values case
                record_fields_tuples_list.append((field_name, '=', field_value))
        return self.env[model_name].search(record_fields_tuples_list, None, limit)

    # In Odoo CSV exports, an 'id' string may refer to a record through the ir_model_data table
    def get_record_id_by_id_string(self, id_string):
        ir_model_data_values = id_string.split('.')
        ir_model_data = self.env["ir.model.data"].search([
            ("module", '=', ir_model_data_values[0]), ("name", '=', ir_model_data_values[1])
        ])
        if ir_model_data:
            return ir_model_data.res_id
        else:
            raise MissingError("No record found for id string " + id_string)
