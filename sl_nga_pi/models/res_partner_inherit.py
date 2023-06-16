from odoo import fields, models, api, _ 

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(
        selection=[('person', 'Brand'), ('company', 'Trader')],
    )
    amount_limit = fields.Float(string="Amount Limit")
    sl_total_due = fields.Float(compute='_compute_sl_total_due')

    def _compute_sl_total_due(self):
        for rec in self:
            move_line = rec.env['account.move.line'].sudo().search([
                ('partner_id', '=', self.id),
                ('parent_state', '=', 'posted'),
                ('account_id.account_type', 'in', ('asset_receivable', 'liability_payable'))
            ])
            if move_line:
                rec.sl_total_due = sum(move_line.mapped('balance'))
            else:
                rec.sl_total_due = 0

    def button_open_sl_total_due(self):
        pass