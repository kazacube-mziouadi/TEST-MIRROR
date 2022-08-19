# -*- coding: utf-8 -*-
{
    'name': 'Convertisseur Excel vers XML',
    'version': '1.0.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Convertis un Excel vers XML',
    'category': 'Base',
    'description': """
        Permet de convertir un fichier Excel vers un fichier XML.
    """,
    'website': 'https://www.myfab.fr/',
    'images': [],
    'depends': [
        'my_fab',
    ],
    'data': [
        'views/mf_xls_configuration.xml',
        'views/mf_xls_config_sheet.xml',
        'views/mf_xls_config_sheet_level.xml',
        'views/mf_xls_config_sheet_field.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'not_show': False,
}
