from openerp import models, fields, api, _, modules
from openerp.exceptions import except_orm


class WoSimpleConsumption(models.TransientModel):
    _inherit = "wo.simple.consumption"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_note = fields.Text(string="Note")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.multi
    def action_validate(self):
        for wiz in self:
            location_rc = wiz.label_id.warehouse_id.production_location_id
            if not location_rc:
                raise except_orm(_('Error'),
                                 _('No production location for the warehouse %s') % (wiz.label_id.warehouse_id.name))

            if wiz.label_id.uom_qty < wiz.qty:
                raise except_orm(_('Error'), _('The quantity can not be greater than that of the label'))

            move_rcs, qty = self.env['stock.move.label'].create_move_label(wiz.label_id, location_dest_id=location_rc,
                                                                           dict_label_qty={wiz.label_id: (wiz.qty, 0)})
            move_rcs.wkf_waiting()
            move_rcs.wkf_done()
            if self.mf_note:
                move_rcs.note = self.mf_note
            if wiz.is_print and wiz.label_id.uom_qty:
                wiz.label_id.do_print_label()

        return True
