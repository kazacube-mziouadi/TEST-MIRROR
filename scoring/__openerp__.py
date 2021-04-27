# -*- coding: utf-8 -*-
{
    'name' : 'Scoring',
    'version' : '0.1.0',
    'author' : 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Manager le risque client et booster la performance commerciale.(En cours de dev)',
    'category' : 'Partner',
    'description' : """Manager le risque client et booster la performance commerciale.(En cours de dev)
    Ce module est en cours de développement.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'advanced',
    'images' : [],
    'depends' : [
        'my_fab'
    ],
    'data': [
        'views/scoring.xml',
        'views/baseMenus.xml',
        'security/scoringSecurity.xml',
        'security/ir.model.access.csv'
    ],
    'qweb' : [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
