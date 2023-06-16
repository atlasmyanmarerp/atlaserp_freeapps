from odoo import models, fields, _, api
from odoo.exceptions import UserError

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    sl_weight_by = fields.Many2one('res.partner', string="Weight By")
    sl_sold_by_fir = fields.Many2one('res.partner', string="Sold by First Person")
    sl_sold_by_sec = fields.Many2one('res.partner', string="Sold by Secound Person")
    sl_total_due_warning = fields.Char()

    def action_confirm(self):
        for rec in self:
            for line in rec.order_line:
                duplicate_lot = rec.order_line.filtered_domain([
                    ('lot_id', '=', line.lot_id.id)
                ])
                if duplicate_lot and len(duplicate_lot) > 1:
                    raise UserError(f"There is same lot for lot {line.lot_id.name}.")
        return super().action_confirm()
    
    @api.onchange('partner_id')
    def _onchange_sl_partner(self):
        for rec in self:
            if not rec.partner_id:
                return
            if rec.partner_id.amount_limit < rec.partner_id.sl_total_due:
                rec.sl_total_due_warning = f'The total due amount of {rec.partner_id.name} is more than the amount limit.'
            else:
                rec.sl_total_due_warning = False
