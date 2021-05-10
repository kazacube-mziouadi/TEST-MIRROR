# -*- coding: utf-8 -*-
{
    'name': 'WipSim Interface',
    'version': '0.1.0',
    'author': 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Interface pour échanger avec le logiciel de pilotage de production WipSim',
    'category': 'Base',
    'description': """Interface pour échanger avec le logiciel de pilotage de production WipSim.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
        'my_fab',
        'affair'
    ],
    'data': [
        'security/wipsim_security.xml',
        'security/ir.model.access.csv',
        'views/wipsim.xml',
        'views/baseMenus.xml'
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
