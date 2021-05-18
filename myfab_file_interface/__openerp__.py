# -*- coding: utf-8 -*-
{
    'name': 'MyFab File Interface',
    'version': '0.1.0',
    'author': 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Interface MyFab pour échanger avec des logiciels externes via fichiers à plat JSON',
    'category': 'Base',
    'description': """Interface MyFab pour échanger avec des logiciels externes via fichiers à plat JSON.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
        'my_fab',
        'affair'
    ],
    'data': [
        'security/myfab_file_interface_security.xml',
        'security/ir.model.access.csv',
        'views/myfab_file_interface.xml',
        'views/baseMenus.xml'
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
