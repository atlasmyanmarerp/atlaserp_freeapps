from odoo import fields, models, _ , api
from odoo.exceptions import UserError

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    owner_id = fields.Many2one('res.partner', string="Owner")
    lot_id = fields.Many2one('stock.lot', string="Lot/Serial")
    available_owner_ids = fields.Many2many('res.partner', string="Available Owners", compute="_get_available_owners")
    available_lot_ids = fields.Many2many('stock.lot', string="Available Lots", compute="_get_available_lots")
    sl_product_tag = fields.Many2many('sl.product.tag', string="Product Tag")
    orighin_sl_weight = fields.Float(string="Origin Weight", default=0)
    sl_weight_loss = fields.Float(string="Weight Loss")
    sl_weight = fields.Float(string="Weight", compute="_compute_weight")
    sl_est_weight = fields.Float(string="Est Weight", default=0.0)
    po_id = fields.Many2one('purchase.order', string="Purchase Order", compute="_compute_purchase_order", store=True)
    po_line_id = fields.Many2one('purchase.order.line', string="Purchase Order Line", compute="_compute_purchase_order", store=True)
    qty_available = fields.Float(string="Available Qty", compute="_compute_qty_available")
    bill_invoice_id = fields.Many2one('account.move', string="Billed Sale")
    bill_move_line_id = fields.Many2one('account.move.line', string="Bill Move Line")

    @api.depends('orighin_sl_weight', 'sl_weight_loss')
    def _compute_weight(self):
        for rec in self:
            rec.sl_weight = rec.orighin_sl_weight - rec.sl_weight_loss

    def _prepare_sl_account_move_line(self, move=False):
        self.ensure_one()
        # aml_currency = move and move.currency_id or self.currency_id
        # date = move and move.date or fields.Date.today()
        return {
            'display_type': self.po_line_id.display_type or 'product',
            'name': '%s: %s' % (self.po_line_id.order_id.name, self.po_line_id.name),
            'product_id': self.po_line_id.product_id.id,
            'product_uom_id': self.po_line_id.product_uom.id,
            'quantity': self.product_uom_qty,
            'price_unit': self.price_unit,
            'est_weight': self.sl_weight,
            'sl_weight': self.sl_weight,
            'est_price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.po_line_id.taxes_id.ids)],
            'analytic_distribution': self.po_line_id.analytic_distribution,
            'purchase_line_id': self.po_line_id.id,
            'sl_sale_line_id': self.id,
            'sl_product_tag': self.sl_product_tag.ids if self.sl_product_tag else False
        }

    @api.depends('order_id.state')
    def add_sold_qty(self):
        for line in self:
            if line.order_id.state == 'sale':
                line.po_line_id.total_sold_qty += line.product_uom_qty
            else:
                pass

    @api.depends('product_id', 'owner_id', 'lot_id')
    def _compute_qty_available(self):
        for line in self:
            qty_available = 0
            if line.product_id and line.product_id.tracking != 'none':
                if line.owner_id and line.lot_id:
                    qty_available = line.product_id.with_context(
                        owner_id=line.owner_id.id,
                        lot_id=line.lot_id.id
                    ).qty_available
                else:
                    pass
            else:
                if line.owner_id:
                    qty_available = line.product_id.with_context(
                        owner_id=line.owner_id.id,
                    ).qty_available
            line.qty_available = qty_available

    @api.constrains('product_uom_qty')
    def constrains_qty(self):
        for line in self:
            if line.product_uom_qty > line.qty_available:
                pass
                # raise UserError("Quantity is greater than available quantity.")

    @api.depends('product_id', 'order_id.warehouse_id')
    def _get_available_owners(self):
        for rec in self:
            quant_ids = self.env['stock.quant'].sudo().search([
                ('product_id', '=', rec.product_id.id),
                ('location_id', '=', rec.order_id.warehouse_id.lot_stock_id.id),
                ('on_hand', '=', True)
            ])
            rec.available_owner_ids = quant_ids.owner_id.ids

    @api.depends('product_id', 'order_id.warehouse_id', 'owner_id')
    @api.onchange('product_id', 'order_id.warehouse_id', 'owner_id')
    def _get_available_lots(self):
        for rec in self:
            quant_ids = self.env['stock.quant'].sudo().search([
                ('product_id', '=', rec.product_id.id),
                ('location_id', '=', rec.order_id.warehouse_id.lot_stock_id.id),
                ('on_hand', '=', True),
                ('owner_id', '=', rec.owner_id.id)
            ])
            quant_ids_deduct = quant_ids
            for quant in quant_ids:
                if not quant.quantity > 0:
                    quant_ids_deduct -= quant
            rec.available_lot_ids = quant_ids_deduct.lot_id.ids

    @api.depends('lot_id', 'order_id.state')
    def _compute_purchase_order(self):
        for line in self:
            po_id = False
            po_line_id = False
            if line.lot_id and line.order_id.state == 'sale':
                move_line_id = self.env['stock.move.line'].sudo().search([
                    ('lot_name', '=', line.lot_id.name),
                    ('picking_code', '=', 'incoming')
                ])
                po_line_id = move_line_id.move_id.purchase_line_id if move_line_id else False
                po_id = po_line_id.order_id if po_line_id else False
            line.po_id = po_id
            line.po_line_id = po_line_id

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        for line in self:
            move_line_id = self.env['stock.move.line'].sudo().search([
                ('lot_name', '=', line.lot_id.name),
                ('picking_code', '=', 'incoming')
            ])
            line.sl_product_tag = move_line_id.sl_product_tag.ids if move_line_id else False

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'sl_weight')
    def _compute_amount(self):
        return super()._compute_amount()

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.order_id.partner_id,
            currency=self.order_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.sl_weight if self.product_id.tracking == 'lot' else self.product_uom_qty,
            discount=self.discount,
            price_subtotal=self.price_subtotal,
        )

    def _prepare_invoice_line(self, **optional_values):
        """Prepare the values to create the new invoice line for a sales order line.

        :param optional_values: any parameter that should be added to the returned invoice line
        :rtype: dict
        """
        res = super()._prepare_invoice_line(**optional_values)
        res.update({
            'sl_weight': self.sl_weight,
            'est_weight':  self.sl_weight,
            'est_price_unit': self.price_unit,
            'sl_product_tag': self.sl_product_tag.ids if self.sl_product_tag else False
        })
        return res