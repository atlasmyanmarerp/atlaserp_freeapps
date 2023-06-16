# -*- coding: utf-8 -*-
{
    'name': "Account Discount",
    'category': 'Inventory',

    'summary': "Discount on Billing"
    'description': "Discount Amount on Bill "

    'author': "Atlas Myanmar ERP",
    'website': "https://www.atlasmyanmarerp.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],
    'live_test_url': 'https://www.youtube.com/watch?v=QCtEe-zsCtQ'

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/account_move_inherit.xml',
        # 'views/purchase_order_inherit_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
