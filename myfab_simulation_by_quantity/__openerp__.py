# -*- coding: utf-8 -*-
{
    'name': 'myfab Simulation par quantités',
    'version': '1.1.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Simulation par quantités',
    'category': 'Advanced',
    'description': """Simulation par quantités.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
        'my_fab',
        'product',
    ],
    'data': [
        'classes/data_intializer/MFDataInitializerSimulationByQuantityTrigger.yml',
        'views/MFSimulationByQuantityLine.xml',
        'views/MFSimulationByQuantity.xml',
        'wizards/simulation_global_value/MFWizardSimulationGlobalValue.xml',
        'wizards/simulation_creation/MFWizardSimulationGenericCreation.xml',
        'wizards/product_info_creation/MFWizardSimulationProductInfoCreation.xml',
        'views/simulation_config/MFSimulationConfig.xml',
        'views/simulation_config/MFSimulationConfigField.xml',
        'views/BaseMenus.xml',
        'views/ProductProduct.xml',
        'views/myfab_simulation_by_quantity_view.xml'
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
