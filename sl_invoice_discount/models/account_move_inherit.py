from odoo import fields, models, api, _ 

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    sl_account_discount = fields.Float(string="Discount Amount", default=0.0)
    sl_acc_discount_per = fields.Float(string="Discount Percentage", default=0)
    sl_discount_type = fields.Selection([
        ('amount', 'Amount'),
        ('percent', 'Percentage')
    ], string="Discount Type", default='amount')

    def update_discount(self):
        if self.invoice_line_ids:
            discount_item_id = self.env.ref('sl_invoice_discount.product_sl_universal_discount').id
            is_discount_line = self.invoice_line_ids.filtered_domain([('product_id', '=', discount_item_id)])
            if is_discount_line:
                is_discount_line.update({
                    'quantity': 1,
                    'price_unit': -(self.compute_sl_discount())
                })
            else:
                self.env['account.move.line'].create({
                    'product_id': discount_item_id,
                    'quantity': 1,
                    'move_id': self._origin.id,
                    'price_unit': -(self.compute_sl_discount())
                })

    def compute_sl_discount(self):
        for rec in self:
            if rec.sl_discount_type == 'percent':
                discount_amount = sum(rec.invoice_line_ids.filtered_domain([
                    ('product_id.detailed_type', '=', 'product')
                ]).mapped('price_subtotal')) if rec.invoice_line_ids else 0
                discount_amount = discount_amount * rec.sl_acc_discount_per
                return discount_amount
            else:
                return rec.sl_account_discount
