# -*- coding: utf-8 -*-
{
    'name': 'MyFab Base',
    'version': '1.1.3',
    'author': 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Initialisation modules et données pour MyFab',
    'category': 'Base',
    'description': """Initialise les modules et données statiques nécessaires à une installation standard.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
        'myfab_file_interface'
    ],
    'data': [
        'classes/DataInitializerMyFabTriggerMF.yml',
        'views/my_fab_web.xml',
        'views/DataInitializerMyFabMF.xml'
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
