from odoo import fields, models, _, api

class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    sl_product_tag = fields.Many2many('sl.product.tag', string="Product Tag")