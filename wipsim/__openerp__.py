# -*- coding: utf-8 -*-
{
    'name' : 'WIPSIM Interface',
    'version' : '0.1.0',
    'author' : 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Interface pour échanger avec le logiciel de pilotage de production WIPSIM',
    'category' : 'Base',
    'description' : """Interface pour échanger avec le logiciel de pilotage de production WIPSIM.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images' : [],
    'depends' : [
        'my_fab'
    ],
    'data': [
        'views/wipsim.xml',
        'views/baseMenus.xml'
    ],
    'qweb' : [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
