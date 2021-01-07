from openerp import models, fields, api, _


class ModelFactory(models.TransientModel):
    _name = 'model.factory.mf'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=64, required=False, help='')

    def create_from_array(self, array, model_name):
        if len(array) < 1:
            return

        column_names = array[0]
        i = 1
        while i < len(array):
            object_elem = {}
            for j in range(len(array[i])):
                object_elem[column_names[j]] = array[i][j]

            self.env[model_name].create(object_elem)
            i += 1
