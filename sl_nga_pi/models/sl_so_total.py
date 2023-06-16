from odoo import models, fields, api, _ 

class SlSoTotalLine(models.Model):
    _name = 'sl.so.total.line'
    _description = "Total Sale Order Line"

    po_id = fields.Many2one('purchase.order', string="Purchase Order")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float("Quantity")
    sl_weight = fields.Float(string="Total Weight")
    price_unit = fields.Float(string="Price Unit")
    price_subtotal = fields.Float(string="Price Subtotal", compute="_compute_amount")
    origin_weight = fields.Float(string="Origin Weight")
    sl_product_tag = fields.Many2many('sl.product.tag', string="Product Tag")

    @api.depends('sl_weight', 'price_unit')
    def _compute_amount(self):
        for line in self:
            if line.product_id.bill_ok or line.product_id.detailed_type != 'product':
                line.price_subtotal = line.quantity * line.price_unit
            else:
                line.price_subtotal = line.sl_weight * line.price_unit