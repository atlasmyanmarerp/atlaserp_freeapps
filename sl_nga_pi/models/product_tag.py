from odoo import fields, models, _, api

class SlProductTag(models.Model):
    _name = "sl.product.tag"
    _description = "Product Tag"

    name = fields.Char("Tag Name")