# -*- coding: utf-8 -*-
{
    'name': 'myfab Base',
    'version': '1.3.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Initialisation modules et données pour myfab',
    'category': 'Base',
    'description': """Initialise les modules et données statiques nécessaires à une installation standard.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
        'myfab_purchase',
        'myfab_production',
        'myfab_logistics',
        'myfab_tools',
        'myfab_file_interface',
        'stock',
        'mrp',
        'calendar',
        'excel_import',
        'printers',
    ],
    'data': [
        'views/my_fab_web.xml',
        'views/config/mf_config.xml',
        'classes/data_initializer/DataInitializerMyFabTriggerMF.yml',
        'views/data_initializer/DataInitializerMyFabMF.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
