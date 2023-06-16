from odoo import fields, models, _, api
from odoo.exceptions import UserError
from datetime import datetime

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockPickingInherit, self).create(vals_list)
        for rec in res:
            po_id = rec.env['purchase.order'].sudo().search([
                ('name', '=', rec.origin)
            ], limit=1)
            if rec.picking_type_code == 'incoming' and po_id and True not in po_id.order_line.mapped('product_id.bill_ok'):
                rec.owner_id = rec.partner_id.id
            else:
                pass
        return res

    def auto_assign_serial(self):
        for rec in self:
            for line in rec.move_line_ids_without_package:
                if not line.product_id.default_code:
                    raise UserError(f"{line.product_id.name} doesn't have interanl reference.")
                if not line.lot_name:
                    seq_code = rec.env['ir.sequence'].next_by_code('lot.auto')
                    line.lot_name = f'{datetime.now().day:02}/{datetime.now().month:02}-{seq_code}'