# -*- coding: utf-8 -*-
{
    'name' : 'myfab multi société',
    'version' : '1.0.0',
    'author' : 'myfab',
    'license': 'Open-prod license',
    'summary': 'multi société par myfab',
    'category' : 'Third party management',
    'description' : """
        Gestion plus complète des échanges en multi société
    """,
    'website': 'https://www.myfab.fr/',
    'module_type': 'advanced',
    'depends' : [
        'my_fab',
        'multi_company_auto',
        'purchase',
        'sale',
    ],
    'data': [
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/stock.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'persistent': False,
}
