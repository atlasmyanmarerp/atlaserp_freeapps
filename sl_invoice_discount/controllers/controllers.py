# -*- coding: utf-8 -*-
# from odoo import http


# class SlSoPoDiscount(http.Controller):
#     @http.route('/sl_so_po_discount/sl_so_po_discount', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sl_so_po_discount/sl_so_po_discount/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sl_so_po_discount.listing', {
#             'root': '/sl_so_po_discount/sl_so_po_discount',
#             'objects': http.request.env['sl_so_po_discount.sl_so_po_discount'].search([]),
#         })

#     @http.route('/sl_so_po_discount/sl_so_po_discount/objects/<model("sl_so_po_discount.sl_so_po_discount"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sl_so_po_discount.object', {
#             'object': obj
#         })
