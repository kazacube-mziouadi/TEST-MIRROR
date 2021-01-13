from openerp import models, fields, api, _
from psycopg2 import DatabaseError


class ModelFactory(models.TransientModel):
    _name = 'model.factory.mf'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=64, required=False, help='')

    def create_from_array(self, array, model_name, convert=[]):
        if len(array) < 1:
            return

        column_names = array[0]
        i = 1
        while i < len(array):
            object_elem = {}
            for j in range(len(array[i])):
                # Conversion de la valeur si besoin
                object_elem[column_names[j]] = array[i][j]
            i += 1
            try:
                self.env[model_name].create(object_elem)
                self.env.cr.commit()
            except DatabaseError:
                self.env.cr.rollback()
                continue

    def convert(self, model_name, column_name_origin, column_origin_value, column_name_destination):
        model = self.env[model_name].search([[column_name_origin, "=", column_origin_value]], None, 1)
        return model[column_name_destination]