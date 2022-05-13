# -*- coding: utf-8 -*-
{
    'name': 'myfab Simulation par quantités',
    'version': '1.0.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Simulation par quantités',
    'category': 'Advanced',
    'description': """Simulation par quantités.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
        'my_fab'
    ],
    'data': [
        'models/MFDataInitializerSimulationByQuantityTrigger.yml',
        'views/MFSimulationByQuantityLine.xml',
        'views/MFSimulationByQuantity.xml',
        'views/wizards/MFWizardSimulationCreation.xml',
        'views/BaseMenus.xml',
        'views/ProductProduct.xml'
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
