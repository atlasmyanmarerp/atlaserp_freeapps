from odoo import api, fields, models, _
from odoo.tools import groupby
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import UserError

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    sl_sale_line_ids = fields.One2many('sale.order.line', 'po_id', string="Sale Order line")
    sl_so_total_line_ids = fields.One2many(
        'sl.so.total.line', 
        'po_id', 
        string="Total Sale Order Line",
        compute="compute_so_total_line"
    )
    sl_create_bill = fields.Boolean(compute='compute_sl_create_bill', string="Create Bill")
    bill_ok = fields.Boolean(string="Can be Billed", compute="compute_bill_ok")
    sl_product_tag = fields.Many2many('sl.product.tag', string="Product Tag")
    partner_city = fields.Char(string="City", related='partner_id.city')
    sl_total_due_warning = fields.Char()

    @api.onchange('partner_id')
    def _onchange_sl_partner(self):
        for rec in self:
            if not rec.partner_id:
                return
            if rec.partner_id.amount_limit < rec.partner_id.sl_total_due:
                rec.sl_total_due_warning = f'The total due amount of {rec.partner_id.name} is more than the amount limit.'
            else:
                rec.sl_total_due_warning = False

    @api.depends('order_line.product_id', 'invoice_status')
    def compute_bill_ok(self):
        for rec in self:
            bill_ok = rec.order_line.mapped('product_id.bill_ok')
            if True in bill_ok and rec.invoice_status not in ('no', 'invoiced'):
                rec.bill_ok = True
            else:
                rec.bill_ok = False

    @api.depends('order_line.total_sold_qty', 'order_line.qty_invoiced')
    def compute_sl_create_bill(self):
        for rec in self:
            if sum(rec.order_line.mapped('total_sold_qty')) > sum(rec.order_line.mapped('qty_invoiced')):
                rec.sl_create_bill = True
            else:
                rec.sl_create_bill = False

    def prepare_so_total_line(self, line, rec):
        return {
            'po_id':rec.id,
            'product_id': line.product_id.id,
            'quantity': line.product_uom_qty,
            'sl_weight': line.sl_weight,
            'price_unit': line.price_unit,
            'origin_weight': line.sl_weight,
            'sl_product_tag': line.sl_product_tag.ids if line.sl_product_tag else False
        }

    @api.depends('sl_sale_line_ids')
    def compute_so_total_line(self):
        so_total = self.env['sl.so.total.line']
        for rec in self:
            if rec.sl_sale_line_ids:
                for line in rec.sl_sale_line_ids:
                    if rec.sl_so_total_line_ids:
                        so_total_line_id = rec.sl_so_total_line_ids.filtered_domain([
                            ('product_id', '=', line.product_id.id),
                            ('origin_weight', '=', line.sl_weight)
                        ])
                        if so_total_line_id:
                            so_total_line_id.update({
                                'quantity': so_total_line_id.quantity + line.product_uom_qty,
                                'sl_weight': so_total_line_id.sl_weight + line.sl_weight,
                                'price_unit': so_total_line_id.price_unit + line.price_unit
                            })
                            if line.sl_product_tag:
                                so_total_line_id.update({
                                    'sl_product_tag': [(4, line.sl_product_tag.ids)]
                                })
                        else:
                            new_line = so_total.create(rec.prepare_so_total_line(line, rec))
                            rec.write({
                                'sl_so_total_line_ids': [(4, new_line.id)]
                            })
                    else:
                        new_line = so_total.create(rec.prepare_so_total_line(line, rec))
                        rec.write({
                            'sl_so_total_line_ids': [(4, new_line.id)]
                        })
            else:
                rec.sl_so_total_line_ids = False
                    
    def button_confirm(self):
        res = super().button_confirm()
        for rec in self:
            for picking_id in rec.picking_ids:
                val_list = []
                vals = {}
                if not picking_id.state in ('done', 'cancel'):
                    picking_id.update(
                        {
                            'move_line_ids_without_package': False
                        }
                    )
                    for move_id in picking_id.move_ids_without_package:
                        if move_id.product_id.tracking == 'lot' and move_id.product_id.upgrade_lots == 'up_lots':
                            for index in range(int(move_id.product_uom_qty)):
                                vals = rec._prepare_move_line_ids(qty=1, qty_done=1, move_id=move_id)
                                val_list.append((0, 0, vals))
                            if int(move_id.product_uom_qty) != move_id.product_uom_qty:
                                float_qty = move_id.product_uom_qty - int(move_id.product_uom_qty)
                                vals = rec._prepare_move_line_ids(qty=float_qty, qty_done=float_qty, move_id=move_id)
                                val_list.append((0, 0, vals))
                        else:
                            vals = rec._prepare_move_line_ids(qty=move_id.product_uom_qty, qty_done=move_id.product_uom_qty, move_id=move_id)
                            val_list.append((0, 0, vals))
                    
                    picking_id.update(
                        {
                            'move_line_ids_without_package': val_list
                        }
                    )
                    picking_id.action_assign()
                    picking_id.auto_assign_serial()
        return res

    def _prepare_move_line_ids(self, qty, qty_done, move_id):
        vals = {}
        vals = {
            'product_id': move_id.product_id.id,
            'sl_product_tag': move_id.purchase_line_id.sl_product_tag.ids,
            # 'product_uom_qty': qty,
            'product_uom_id': move_id.product_uom.id,
            'qty_done': qty_done,
            'location_id': move_id.location_id.id,
            'location_dest_id': move_id.location_dest_id.id
        }
        return vals
    
    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        sequence = 10
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            is_bill = order.order_line.mapped('product_id.bill_ok')
            if True in is_bill:
                for line in order.order_line:
                    if line.display_type == 'line_section':
                        pending_section = line
                        continue
                    if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                        if pending_section:
                            line_vals = pending_section._prepare_account_move_line()
                            line_vals.update({'sequence': sequence})
                            invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                            sequence += 1
                            pending_section = None
                        line_vals = line._prepare_account_move_line()
                        line_vals.update({'sequence': sequence})
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                        sequence += 1
                invoice_vals_list.append(invoice_vals)
            else:
                if not order.sl_sale_line_ids:
                    raise UserError("Nothing to Invoice.")
                to_bill_sale_ids = order.sl_sale_line_ids
                move_line_ids = self.env['account.move.line'].sudo().search([
                    ('sl_sale_line_id', 'in', to_bill_sale_ids.ids)
                ])
                to_bill_sale_ids = to_bill_sale_ids - move_line_ids.sl_sale_line_id
                for line in to_bill_sale_ids:
                    line_vals = line._prepare_sl_account_move_line()
                    line_vals.update({'sequence': sequence})
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                    sequence += 1
                service_product = order.order_line.filtered_domain([
                    ('product_id.detailed_type', '=', 'service'),
                    ('qty_invoiced', '!=', 'product_qty')
                ])
                if service_product:
                    for ser in service_product:
                        line_vals = ser._prepare_sl_account_move_line()
                        line_vals.update({'sequence': sequence})
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                        sequence += 1
                invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()
        return self.action_view_invoice(moves)
    
    def name_get(self):
        res = []
        for order in self:
            name = f"{order.name} [{order.partner_id.name}]"
            res.append((order.id, name))
        return res

class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    total_sold_qty = fields.Float(string="Total Sold", compute="compute_total_sold")

    @api.depends('order_id.sl_sale_line_ids')
    def compute_total_sold(self):
        for line in self:
            if line.order_id.sl_sale_line_ids:
                sale_ids = line.order_id.sl_sale_line_ids.filtered_domain([
                    ('product_id', '=', line.product_id.id)
                ])
                if sale_ids:
                    line.total_sold_qty = sum(sale_ids.mapped('product_uom_qty'))
                else:
                    line.total_sold_qty = 0
            else:
                line.total_sold_qty = 0

    def _prepare_sl_account_move_line(self, move=False):
        self.ensure_one()
        # aml_currency = move and move.currency_id or self.currency_id
        # date = move and move.date or fields.Date.today()
        return {
            'display_type': self.display_type or 'product',
            'name': '%s: %s' % (self.order_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.product_qty,
            'price_unit': 0,
            # 'est_weight': self.sl_weight,
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_distribution': self.analytic_distribution,
            'purchase_line_id': self.id
        }
    
    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        res.update({
            'sl_product_tag': self.sl_product_tag.ids if self.sl_product_tag else False
        })
