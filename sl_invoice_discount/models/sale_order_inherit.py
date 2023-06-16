from odoo import fields, models, api, _ 

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    sl_sale_discount = fields.Float(string="Discount Amount", default=0.0)
    sl_so_discount_per = fields.Float(string="Discount Percentage", default=0)
    sl_discount_type = fields.Selection([
        ('amount', 'Amount'),
        ('percent', 'Percentage')
    ], string="Discount Type", default='amount')

    def update_discount(self):
        if self.order_line:
            discount_item_id = self.env.ref('sl_so_po_discount.product_sl_universal_discount').id
            is_discount_line = self.order_line.filtered_domain([('product_id', '=', discount_item_id)])
            if is_discount_line:
                is_discount_line.update({
                    'product_uom_qty': 1,
                    'price_unit': -(self.compute_sl_discount())
                })
            else:
                self.env['sale.order.line'].create({
                    'product_id': discount_item_id,
                    'product_uom_qty': 1,
                    'order_id': self._origin.id,
                    'price_unit': -(self.compute_sl_discount())
                })

    def compute_sl_discount(self):
        for rec in self:
            if rec.sl_discount_type == 'percent':
                discount_amount = sum(rec.order_line.filtered_domain([
                    ('product_id.detailed_type', '=', 'product')
                ]).mapped('price_subtotal')) if rec.order_line else 0
                discount_amount = discount_amount * rec.sl_so_discount_per
                return discount_amount
            else:
                return rec.sl_sale_discount