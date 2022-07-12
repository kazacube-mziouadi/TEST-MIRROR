# -*- coding: utf-8 -*-
{
    'name': 'myfab Appel d\'offre',
    'version': '1.0.1',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Appel d\'offre myfab pour améliorer le module existant.',
    'category': 'Purchase and supply',
    'description': """Ajout d'une typologie de document pour gérer les documents produits dans les mails des appels d'offres""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'advanced',
    'images': [],
    'depends': [
        'my_fab',
        'call_tender',
        'mrp',
        'sale_purchase'
    ],
    'data': [
        'views/product.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'not_show': False
}
