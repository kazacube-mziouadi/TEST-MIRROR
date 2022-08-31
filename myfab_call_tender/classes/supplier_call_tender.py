# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import except_orm, ValidationError

class supplier_call_tender(models.Model):
    _inherit = 'supplier.call.tender'

    @api.multi
    def action_send_mail(self):
        call_tender_rc = self.tender_id
        if not call_tender_rc.mf_document_ids:
            return super(supplier_call_tender, self).action_send_mail()

        attachment_ids = []
        # Copy of the original code because we add the document attachment to the list
        name, binary = self.generate_binary()
        data_attach = {
            'type': 'binary',
            'res_model': 'supplier.call.tender', 
            'res_id': self.id, 
            'name': name , 
            'datas': binary, 
            'datas_fname': name
        }
        attachment_ids.append(self.env['ir.attachment'].create(data_attach).id)

        # new code to add the documents to the mail attachment
        for mf_document_id in call_tender_rc.mf_document_ids:
            #Création des PJ
            #/!\ Pas de res_id parce qu'on ne veut pas lier la PJ à l'achat/la vente /!\
            data_attach = {
                'type': 'binary',
                'res_model': 'call.tender', 
                #'res_id': call_tender_rc.id, # we don't use the res_id to not attach documents to the model in the view
                'name': mf_document_id.name , 
                'datas': mf_document_id.attachment, 
                'datas_fname': mf_document_id.name
            }
            attachment_ids.append(self.env['ir.attachment'].create(data_attach).id)

        # copy of the original code next lines
        context = self.env.context.copy()
        if context.get('default_attachment_ids', False):
            context['default_attachment_ids'].append(attachment_ids)
        else:
            context.update({'default_attachment_ids': attachment_ids})
            
        return self.env['mail.message'].with_context(context).action_send_mail(self.supplier_id, 'supplier.call.tender', '',self.id)