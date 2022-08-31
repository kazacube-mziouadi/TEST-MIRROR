# -*- coding: utf-8 -*-
{
    'name': 'myfab IceScrum Connector',
    'version': '1.0.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Connecteur myfab vers IceScrum',
    'category': 'Base',
    'description': """Connecteur myfab vers IceScrum.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'advanced',
    'images': [],
    'depends': [
        'my_fab',
    ],
    'data': [
        'views/CalendarEvent.xml',
        'wizards/MfWizardImportIceScrum.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
