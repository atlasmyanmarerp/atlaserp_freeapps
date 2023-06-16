from odoo import fields, models, api, _ 

class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    sl_service_type = fields.Selection(string="Service Type", related='product_tmpl_id.sl_service_type')
    bill_ok = fields.Boolean(string="Can be Billed", related='product_tmpl_id.bill_ok')