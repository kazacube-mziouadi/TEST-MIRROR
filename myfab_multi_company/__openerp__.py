# -*- coding: utf-8 -*-
{
    'name' : 'myfab Multi société',
    'version' : '1.0.0',
    'author' : 'myfab',
    'license': 'Open-prod license',
    'summary': 'Multi société par myfab',
    'category' : 'Third party management',
    'description' : """
        Gestion plus complète de la fonctionnalité de multi société
    """,
    'website': 'https://www.myfab.fr/',
    'module_type': 'advanced',
    'depends' : [
        'my_fab',
        'multi_company_auto',
        'kit_purchase',
        'kit_sale',
        'purchase',
    ],
    'data': [
        'views/purchase_order.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'persistent': True,
}
