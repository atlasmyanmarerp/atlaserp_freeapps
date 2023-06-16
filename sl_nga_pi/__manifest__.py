# -*- coding: utf-8 -*-
{
    'name': "Consignment-based fish market",
    'category': 'Inventory, Purchae, Sales, Invoicing Management',
    'version': '16.0',
    'summary': "Consignment-base fish market business flow",
    'description': "Consignment-based Inventory Management System, Integrated with Purchase and Sales",
    'support': "atlasmyanmarerp@gmail.com",
    'author': "Atlas Myanmar ERP",
    'website': "https://www.atlasmyanmarerp.com",
    'live_test_url': 'https://www.youtube.com/watch?v=QCtEe-zsCtQ',
    'depends': ['base', 'sale', 'stock', 'purchase', 'account', 'base_accounting_kit'],





    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/product_tag_view.xml',
        'views/templates.xml',
        'views/sale_order_inherit_view.xml',
        'views/purchase_order_inherit_view.xml',
        'views/stock_picking_inherit_view.xml',
        'views/stock_move_line_inherit_view.xml',
        'views/product_template_inherit_view.xml',
        'views/account_move_inherit_view.xml',
        'views/res_partner_inherit_view.xml',

        'reports/purchase_custom_rp.xml',
        'reports/report_action.xml',
        'reports/actual_invoice.xml',
        'reports/custom_invoice.xml',
        'views/menuitems.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
