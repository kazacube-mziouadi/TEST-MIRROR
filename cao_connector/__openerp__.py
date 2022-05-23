# -*- coding: utf-8 -*-
{
    'name': 'Connecteur CAO myfab',
    'version': '1.0.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Connecteur CAO via import XML',
    'category': 'Base',
    'description': """
        Permet lors de l\'import XML, de comparer les produits et nomenclatures aux éléments existants similaires.
        Ainsi les éléments importés ne vont pas simplement écraser les données. Cela permet une mise à jour plus fine des desriptions.
    """,
    'website': 'https://www.myfab.fr/',
    'module_type': 'advanced',
    'images': [],
    'depends': [
        'my_fab',
        'xml_import',
    ],
    'data': [
        'views/xml_import_processing.xml',
        'wizards/bom_comparator/xml_import_bom_comparator.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
