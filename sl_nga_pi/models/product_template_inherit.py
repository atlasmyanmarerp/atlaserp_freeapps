from odoo import fields, models, api, _ 

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    upgrade_lots = fields.Selection([
        ('up_lots', 'By Upgrade Lots'),
        ('def_lots', 'By Default Lots'),
    ], string="Upgrade Lots", 
    default='def_lots')

    sl_service_type = fields.Selection([
        ('bag', 'ဂုန်နီ+အတွင်းခံ+အိတ်'),
        ('other', 'ခါ+တူ+ချုပ်+လှယ်'),
        ('tansar', 'ဂိတ်ပို့ + ကားတန်ဆာ'),
        ('labour', 'လုပ်သားခ'),
        ('salt', 'ဆားဖိုး'),
        ('tape', 'ဖော့ + တိတ်'),
        ('basket', 'ခြင်း + တောင်း'),
        ('service_charges', 'ပြုပြင်စရိတ်')
    ], string="Service Type", default=False)

    bill_ok = fields.Boolean(string="Can be Billed")