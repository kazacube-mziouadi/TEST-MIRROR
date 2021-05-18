# -*- coding: utf-8 -*-
{
    'name': 'MyFab base',
    'version': '0.1.0',
    'author': 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Modules de base pour MyFab',
    'category': 'Base',
    'description': """Regroupe tous les modules de base pour MyFab.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
        'base_setup',
        'base_openprod',
        'l10n_fr',
        'mrp'
    ],
    'data': [
        'WizardInstallerTriggerMF.yml',
        'WizardInstallerMF.xml',
        'views/modules.xml',
        'views/my_fab_web.xml'
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
