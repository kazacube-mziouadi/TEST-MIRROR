# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class octopart_seller_partner_connect(models.TransientModel):
    _name = 'octopart.seller.partner.connect'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    seller_id = fields.Many2one('octopart.seller', string="Seller", required=True)    
    partner_id = fields.Many2one('res.partner', 'Partner', ondelete='cascade', required=True, domain = "[('is_supplier','=',True), ('octopart_uid_seller','=','0')]")
    is_seller_id_set = fields.Boolean()

    #===========================================================================
    # Auto call functions
    #===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(octopart_seller_partner_connect, self).default_get(fields_list=fields_list)
        
        seller_id = False
        res['is_seller_id_set'] = seller_id

        context = self.env.context
        if context.get('active_id', False):
            active_model_rs = self.env[context.get('active_model', '')].browse(context['active_id'])
            if context.get('active_model', '') == 'octopart.seller':
                seller_id = active_model_rs
            elif context.get('active_model', '') == 'octopart.product':
                seller_id = active_model_rs.seller_id

        if seller_id:
            res['seller_id'] = seller_id.id
            res['is_seller_id_set'] = True
            partner_id = self._get_associated_partner(seller_id)
            if partner_id:
                res['partner_id'] = partner_id.id
        
        return res

    @api.onchange('seller_id')
    def _onchange_get_partner_id(self):
        if self.seller_id:
            self.partner_id = self._get_associated_partner(self.seller_id)

    def _get_partner_ids(self, octopart_uid):
        if octopart_uid > 0:
            partner_ids = self.env['res.partner'].search([("octopart_uid_seller", '=', octopart_uid)])
            return partner_ids
        return False

    def _get_associated_partner(self, seller_id):
        if seller_id and seller_id.octopart_uid > 0:
            partner_rc = self._get_partner_ids(seller_id.octopart_uid)
            if partner_rc:
                return partner_rc
        return False

    #===========================================================================
    # Actions
    #===========================================================================
    @api.one
    def add_seller_id(self):
        self._clear_all_associated_partners()
        self._update_partner(self.partner_id,self.seller_id.octopart_uid)

    def _clear_all_associated_partners(self):
        partner_rcs = self._get_partner_ids(self.seller_id.octopart_uid)
        for partner_id in partner_rcs:
            self._update_partner(partner_id,0)

    def _update_partner(self, partner_id, octopart_uid):
        if partner_id:
            partner_id.write({'octopart_uid_seller' : octopart_uid })
