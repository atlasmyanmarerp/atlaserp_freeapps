# -*- coding: utf-8 -*-
{
    'name': "Account Discount",
    'category': 'Inventory',

    'summary': "Discount on Billing",
    'description': "Discount Amount on Bill ",

    'author': "Atlas Myanmar ERP",
    'website': "https://www.atlasmyanmarerp.com",
    'version': '16.0',
    'depends': ['base', 'account'],
    'live_test_url': 'https://www.youtube.com/watch?v=QCtEe-zsCtQ',
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/account_move_inherit.xml',
        # 'views/purchase_order_inherit_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
