from odoo import fields, models, api, _ 

class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    sl_weight = fields.Float(string="Weight", default=0.0)
    est_weight = fields.Float(string="Org Weight", default=0.0)
    sl_sale_line_id = fields.Many2one('sale.order.line',string="Sl Sale Line")
    est_price_unit = fields.Float(string="Org Price")
    sl_product_tag = fields.Many2many('sl.product.tag', string="Product Tag")

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super().create(vals_list)
    #     for rec in res:
    #         if rec.sl_sale_line_id and rec.move_id.move_type == 'in_invoice':
    #             rec.sl_sale_line_id.bill_move_line_id = rec.id
    #     return res

    @api.depends('sl_sale_line_id')
    def add_sale_line_id(self):
        for line in self:
            if line.sl_sale_line_id:
                line.sl_sale_line_id.bill_invoice_id = line.move_id.id

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'sl_weight')
    def _compute_totals(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False
            # Compute 'price_subtotal'.
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
            if (line.sale_line_ids or line.purchase_order_id) and line.product_id.detailed_type == 'product' and not line.product_id.bill_ok:
                subtotal = line_discount_price_unit * line.sl_weight
            else:
                subtotal = line_discount_price_unit * line.quantity
            # Compute 'price_total'.
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.sl_weight if line.product_id.detailed_type == 'product' and not line.product_id.bill_ok else line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res['total_excluded']
                line.price_total = taxes_res['total_included']
            else:
                line.price_total = line.price_subtotal = subtotal

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.
        :return: A python dictionary.
        """
        self.ensure_one()
        is_invoice = self.move_id.is_invoice(include_receipts=True)
        sign = -1 if self.move_id.is_inbound(include_receipts=True) else 1
        if self.sl_weight and self.product_id.detailed_type == 'product' and not self.product_id.bill_ok:
            qty = self.sl_weight
        elif is_invoice:
            qty = self.quantity
        else:
            qty = 0
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.partner_id,
            currency=self.currency_id,
            product=self.product_id,
            taxes=self.tax_ids,
            price_unit=self.price_unit if is_invoice else self.amount_currency,
            quantity=qty,
            discount=self.discount if is_invoice else 0.0,
            account=self.account_id,
            analytic_distribution=self.analytic_distribution,
            price_subtotal=sign * self.amount_currency,
            is_refund=self.is_refund,
            rate=(abs(self.amount_currency) / abs(self.balance)) if self.balance else 1.0
        )