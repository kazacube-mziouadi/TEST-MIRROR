# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class octopart_seller_partner_associate(models.TransientModel):
    _name = 'octopart.seller.partner.associate'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    octopart_seller_id = fields.Many2one('octopart.seller', string="Seller", required=True)    
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='cascade', required=True, domain = "[('is_supplier','=',True), ('octopart_uid_seller_id','=',False)]")
    is_seller_set = fields.Boolean()

    #===========================================================================
    # Auto call functions
    #===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(octopart_seller_partner_associate, self).default_get(fields_list=fields_list)
        
        octopart_seller_id = False
        res['is_seller_set'] = octopart_seller_id

        context = self.env.context
        if context.get('active_id', False):
            active_model_rs = self.env[context.get('active_model', '')].browse(context['active_id'])
            if context.get('active_model', '') == 'octopart.seller':
                octopart_seller_id = active_model_rs
            elif context.get('active_model', '') == 'octopart.product.research':
                octopart_seller_id = active_model_rs.octopart_seller_id

        if octopart_seller_id:
            res['octopart_seller_id'] = octopart_seller_id.id
            res['is_seller_set'] = True
            partner_id = self._get_associated_partner(octopart_seller_id)
            if partner_id:
                res['partner_id'] = partner_id.id
        
        return res

    @api.onchange('octopart_seller_id')
    def _onchange_get_partner_id(self):
        if self.octopart_seller_id:
            self.partner_id = self._get_associated_partner(self.octopart_seller_id)

    def _get_partner_ids(self, octopart_seller_id_id):
        if octopart_seller_id_id > 0:
            return self.env['res.partner'].search([("octopart_uid_seller_id", '=', octopart_seller_id_id)])
        return False

    def _get_associated_partner(self, octopart_seller_id):
        if octopart_seller_id and octopart_seller_id.octopart_uid > 0:
            partner_rc = self._get_partner_ids(octopart_seller_id.id)
            if partner_rc:
                return partner_rc
        return False

    #===========================================================================
    # Actions
    #===========================================================================
    @api.one
    def add_seller_id(self):
        self._clear_all_associated_partners()
        self._update_partner(self.partner_id,self.octopart_seller_id.id)

    def _clear_all_associated_partners(self):
        partner_rcs = self._get_partner_ids(self.octopart_seller_id.id)
        for partner_id in partner_rcs:
            # Writing False in the octopart_uid_seller_id is like doing "unlink" but this permits to reuse the same method
            self._update_partner(partner_id,False)

    def _update_partner(self, partner_id, octopart_seller_id):
        if partner_id:
            partner_id.write({'octopart_uid_seller_id' : octopart_seller_id })
