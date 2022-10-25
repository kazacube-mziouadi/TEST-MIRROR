# -*- coding: utf-8 -*-
{
    'name': 'Connecteur CAO myfab',
    'version': '1.1.2',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Connecteur CAO via import XML',
    'category': 'Base',
    'description': """
        Permet lors de l\'import XML, de comparer les produits et nomenclatures aux éléments existants similaires.
        Ainsi les éléments importés ne vont pas simplement écraser les données. Cela permet une mise à jour plus fine des descriptions.
    """,
    'website': 'https://www.myfab.fr/',
    'module_type': 'advanced',
    'images': [],
    'depends': [
        'myfab_xlsx_to_xml',
        'my_fab',
        'xml_import',
    ],
    'data': [
        'security/ir.model.access.csv',
        'classes/data_initializer/MFDataInitializerCAOConnectorTrigger.yml',
        'views/sequence/xml_import_processing.xml',
        'views/config/mf_config.xml',
        'views/myfab_cao_connector_web.xml',
        'views/processing/xml_preprocessing_table_rule.xml',
        'views/processing/xml_preprocessing.xml',
        'views/processing/xml_import_configuration_table.xml',
        'views/processing/xml_import_processing.xml',
        'views/processing/xml_import_processing_sim_action.xml',
        'views/myfab_cao_xlsx_menu.xml',
        'wizards/processing/mf_xml_import_processing_wizard.xml',
        'views/myfab_cao_connector_global_menu.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
