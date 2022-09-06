# -*- coding: utf-8 -*-
{
    'name': 'Convertisseur XLSX vers XML',
    'version': '1.0.1',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Convertis un XLSX vers XML',
    'category': 'Base',
    'description': """
        Permet de convertir un fichier XLSX vers un fichier XML.
    """,
    'website': 'https://www.myfab.fr/',
    'images': [],
    'depends': [
        'my_fab',
    ],
    'data': [
        'security/myfab_cao_connector_security.xml',
        'security/ir.model.access.csv',
        'views/config/mf_xlsx_configuration.xml',
        'views/config/mf_xlsx_config_sheet.xml',
        'views/config/mf_xlsx_config_sheet_level.xml',
        'views/config/mf_xlsx_config_sheet_field.xml',
        'views/convert/mf_xlsx_convert_to_xml.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'not_show': True,
}
