# -*- coding: utf-8 -*-
# from odoo import http


# class SlNgaPi(http.Controller):
#     @http.route('/sl_nga_pi/sl_nga_pi', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sl_nga_pi/sl_nga_pi/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sl_nga_pi.listing', {
#             'root': '/sl_nga_pi/sl_nga_pi',
#             'objects': http.request.env['sl_nga_pi.sl_nga_pi'].search([]),
#         })

#     @http.route('/sl_nga_pi/sl_nga_pi/objects/<model("sl_nga_pi.sl_nga_pi"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sl_nga_pi.object', {
#             'object': obj
#         })
