# -*- coding: utf-8 -*-

from openerp import models, api, fields, report
from openerp.tools.translate import _
from openerp.addons.base_openprod.common import get_form_view
from openerp.exceptions import except_orm, ValidationError

# If cStringIO is available, we use it
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
class mail_message(models.Model):
    _inherit = 'mail.message'
        
    def action_send_mail(self, email_to, model, edi_select, object_id, mail_id=False, update_context_other=None, forced_email_to=False):
        """
            Surcharge de la méthode d'envoi de mail pour ajouter les éventuels plans et controles en
            PJ
        """
        product_id_list = []
        quality_obj = self.env['stock.quality.control']
        attachment_obj = self.env['ir.attachment']
        att_ids = []
        pdf_type = ''
        attachment_datas = {}
        res = super(mail_message, self).action_send_mail(email_to, model, edi_select, object_id, mail_id=mail_id, update_context_other=update_context_other, forced_email_to=forced_email_to)
        if not res.get('context'):
            res['context'] = {}
        
        #Récupération ids des produits de l'appel d'offre
        if model == 'supplier.call.tender':
            supplier_call_tender_rs = self.env['supplier.call.tender'].browse(object_id)
            if supplier_call_tender_rs:
                call_tender_rs = supplier_call_tender_rs.tender_id
                product_id_list = call_tender_rs and [product_ids.product_id.id for product_ids in call_tender_rs.product_ids] or []
                pdf_type = 'mf_pdf_call_tender_mail'
                res['context']['default_model'] = model

        
        for product_id in product_id_list:
            #Recherche des plans et controles
            printed_doc_list = quality_obj.search([('product_id', '=', product_id), 
                                                   ('type', '=', pdf_type), ('pdf_file', '!=', False)])
            for printed_doc in printed_doc_list:
                if printed_doc.type == pdf_type:
                    attachment_datas[printed_doc.pdf_file.fname] = printed_doc.pdf_file.attachment
        
        for name, attach_data in attachment_datas.iteritems():
            #Création des PJ
            #Pas de res_id parce qu'on ne veut pas lier la PJ à l'achat/la vente
            data_attach = {
                'name': name,
                'datas': attach_data,
                'datas_fname': name,
                'description': name,
                'res_model' : model,
            }
            att_ids.append(attachment_obj.create(data_attach).id)
            
        if res['context'].get('default_attachment_ids'):
            res['context']['default_attachment_ids'].extend(att_ids)
        else:
            res['context']['default_attachment_ids'] = att_ids
        
#         res['context']['no_mail_onchange'] = True
        return res
