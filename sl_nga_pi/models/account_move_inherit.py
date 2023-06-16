from odoo import fields, models, api, _ 

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    sl_inv_line_ids = fields.One2many(
        'sl.inv.line', 
        'inv_move_id',
        string="Sl Invoice Line"
    )
    sl_inv_line_sec_ids = fields.One2many(
        'sl.inv.line.sec', 
        'inv_move_id',
        string="Sec Sl Invoice Line"
    )
    sl_po_id = fields.Many2one('purchase.order', string="Purchase Order")
    sl_partner_id = fields.Many2one('res.partner', related='sl_po_id.partner_id')
    sl_car_no = fields.Char(string="Car No.")
    sl_driver_name = fields.Char(string="Driver Name")
    sl_station = fields.Char(string="Station")
    before_total_due = fields.Monetary(string="အကြွေးရှိ", compute="_compute_total_due")
    after_total_due = fields.Monetary(string="ကြွေးလက်ကျန်", compute="_compute_total_due")
    is_tag = fields.Boolean(compute='_compute_is_tag')

    @api.depends('invoice_line_ids.sl_product_tag')
    def _compute_is_tag(self):
        for rec in self:
            tag_ids = rec.invoice_line_ids.mapped('sl_product_tag')
            if tag_ids:
                rec.is_tag = True
            else:
                rec.is_tag = False


    @api.depends('partner_id', 'amount_paid', 'amount_total')
    def _compute_total_due(self):
        for rec in self:
            if rec.partner_id:
                rec.after_total_due = rec.partner_id.total_due
                rec.before_total_due = rec.partner_id.total_due + rec.amount_total
            else:
                rec.after_total_due = 0
                rec.before_total_due = 0
    
    def action_add_service_product(self):
        for rec in self:
            po_id = rec.line_ids.mapped('purchase_line_id').order_id if rec.line_ids and rec.move_type=="in_invoice" else False
            if po_id:
                move_ids = rec.env['account.move'].sudo().search([
                    ('sl_po_id', '=', po_id.id),
                    ('state', '!=', 'cancel')
                ])
                if move_ids:
                    move_line = self.env['account.move.line']
                    line_ids = move_ids.line_ids.filtered_domain([
                        ('product_id.detailed_type', '=', 'service')
                    ])
                    for line_id in line_ids:
                        line = move_line.create({
                            'product_id': line_id.product_id.id,
                            'quantity': line_id.quantity,
                            'price_unit': -line_id.price_unit,
                            'move_id': rec.id,
                            'est_price_unit': -line_id.price_unit
                        })
                        rec.line_ids = [(4, line.id)]
            pass

    def action_post(self):
        res = super().action_post()
        sl_inv_line = self.env['sl.inv.line']
        SecSlvLine = self.env['sl.inv.line.sec']
        for rec in self:
            rec.sl_inv_line_ids = False
            for line in rec.invoice_line_ids:
                if rec.sl_inv_line_ids:
                    rec_line = rec.sl_inv_line_ids.filtered_domain([
                        ('product_id', '=', line.product_id.id),
                        ('org_price_unit', '=', line.price_unit)
                    ])
                    if rec_line:
                        rec_line.write({
                            'quantity': rec_line.quantity + line.quantity,
                            'sl_weight': rec_line.sl_weight + line.sl_weight,
                            'price_unit': rec_line.price_unit + line.price_unit
                        })
                        if line.sl_product_tag:
                            for tag in line.sl_product_tag:
                                if tag not in rec_line.sl_product_tag:
                                    rec_line.write({
                                        'sl_product_tag': [(4, line.tag.id)]
                                    })
                    else:
                        new_line = sl_inv_line.create(rec.prepare_sl_inv_line(line))
                        rec.write({
                                'sl_inv_line_ids': [(4, new_line.id)]
                            })
                else:
                    new_line = sl_inv_line.create(rec.prepare_sl_inv_line(line))
                    rec.write({
                            'sl_inv_line_ids': [(4, new_line.id)]
                        })
            rec.sl_inv_line_sec_ids = False
            for sl_line in rec.sl_inv_line_ids:
                sec_sl_line = SecSlvLine.sudo().create({
                    'inv_move_id': rec.id,
                    'product_id': sl_line.product_id.id,
                    'quantity': sl_line.quantity,
                    'sl_weight': sl_line.sl_weight,
                    'price_unit': sl_line.price_unit,
                    'org_price_unit': sl_line.org_price_unit,
                    'sl_product_tag': sl_line.sl_product_tag.ids if sl_line.sl_product_tag else False
                })
                rec.write({
                            'sl_inv_line_sec_ids': [(4, sec_sl_line.id)]
                        })
        return res

    def prepare_sl_inv_line(self, line):
        return {
            'inv_move_id': self.id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
            'sl_weight': line.sl_weight,
            'price_unit': line.price_unit,
            'org_price_unit': line.price_unit,
            'sl_product_tag': line.sl_product_tag.ids if line.sl_product_tag else False
        }