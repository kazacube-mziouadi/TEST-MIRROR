# -*- coding: utf-8 -*-
{
    'name': 'MyFab Configurateur',
    'version': '1.0.0',
    'author': 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Configurateur MyFab pour améliorer le configurateur existant.',
    'category': 'Product',
    'description': """Configurateur MyFab qui enrichis le module existant.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'advanced',
    'images': [],
    'depends': [
        'my_fab',
        'variants',
    ],
    'data': [
        'views/mrp_option.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'not_show': False
}
