# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import except_orm, ValidationError

class supplier_call_tender(models.Model):
    _inherit = 'supplier.call.tender'

    @api.multi
    def action_send_mail(self):
        call_tender_rc = self.tender_id
        if len(call_tender_rc.mf_document_ids) <= 0:
            return super(supplier_call_tender, self).action_send_mail()

        # Copy of the original code because we add the document attachment to the list
        name, binary = self.generate_binary()
        attachment_rcs = self.env['ir.attachment'].create({
            'type': 'binary',
            'res_model': 'supplier.call.tender', 
            'res_id': self.id, 
            'name': name , 
            'datas': binary, 
            'datas_fname': name
        })

        # new code to add the documents to the mail attachment
        attachment_rc = self.env['ir.attachment']
        for mf_document_id in call_tender_rc.mf_document_ids:
            #Création des PJ
            #Pas de res_id parce qu'on ne veut pas lier la PJ à l'achat/la vente
            data_attach = {
                'type': 'binary',
                'res_model': 'call.tender', 
                'res_id': call_tender_rc.id, 
                'name': mf_document_id.name , 
                'datas': mf_document_id.attachment, 
                'datas_fname': mf_document_id.name
            }
            attachment_rcs.append(attachment_rc.create(data_attach).id)

        # copy of the original code next lines
        context = self.env.context.copy()
        if context.get('default_attachment_ids', False):
            context['default_attachment_ids'].append(attachment_rcs.ids)
        else:
            context.update({'default_attachment_ids': attachment_rcs.ids})
            
        return self.env['mail.message'].with_context(context).action_send_mail(self.supplier_id, 'supplier.call.tender', '',self.id)