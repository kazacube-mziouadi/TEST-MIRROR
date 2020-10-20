# -*- coding: utf-8 -*-
{
    'name' : 'Scoring',
    'version' : '0.1.0',
    'author' : 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Score les entreprises.(En cours de dev)',
    'category' : 'Partner',
    'description' : """Permet de connaitre la solvabilite des entreprises.
    Ce module est en cours de developpement.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'optional',
    'images' : [],
    'depends' : [
        'partner_openprod'
    ],
    'data': [
        'views/scoring.xml'
    ],
    'qweb' : [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
