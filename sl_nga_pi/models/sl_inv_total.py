from odoo import models, fields, api, _ 

class SlInvLine(models.Model):
    _name = 'sl.inv.line'
    _description = "Total invoice Line"

    inv_move_id = fields.Many2one('account.move', string="Purchase Order")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float("Quantity")
    sl_weight = fields.Float(string="Total Weight")
    price_unit = fields.Float(string="Total Price Unit")
    org_price_unit = fields.Float(string="Price Unit")
    price_subtotal = fields.Float(string="Price Subtotal", compute="_compute_amount")
    sl_product_tag = fields.Many2many('sl.product.tag', string="Product Tag")
    display_tag = fields.Char(compute='_compute_display_tag')

    @api.depends('sl_product_tag')
    def _compute_display_tag(self):
        for rec in self:
            rec.display_tag = ', '.join(tag.name for tag in rec.sl_product_tag)

    @api.depends('sl_weight', 'price_unit', 'org_price_unit')
    def _compute_amount(self):
        for line in self:
            if line.product_id.detailed_type != "product" or line.product_id.bill_ok:
                line.price_subtotal = line.quantity * line.org_price_unit
            else: 
                line.price_subtotal = line.sl_weight * line.org_price_unit

class SlInvLineSec(models.Model):
    _name = 'sl.inv.line.sec'
    _description = "Second Total invoice Line"

    inv_move_id = fields.Many2one('account.move', string="Purchase Order")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float("Quantity")
    sl_weight = fields.Float(string="Total Weight")
    price_unit = fields.Float(string="Total Price Unit")
    org_price_unit = fields.Float(string="Price Unit")
    price_subtotal = fields.Float(string="Price Subtotal", compute="_compute_amount")
    sl_product_tag = fields.Many2many('sl.product.tag', string="Product Tag")
    display_tag = fields.Char(compute='_compute_display_tag')

    @api.depends('sl_product_tag')
    def _compute_display_tag(self):
        for rec in self:
            rec.display_tag = ', '.join(tag.name for tag in rec.sl_product_tag)

    @api.depends('sl_weight', 'price_unit', 'org_price_unit')
    def _compute_amount(self):
        for line in self:
            if line.product_id.detailed_type != "product" or line.product_id.bill_ok:
                line.price_subtotal = line.quantity * line.org_price_unit
            else: 
                line.price_subtotal = line.sl_weight * line.org_price_unit