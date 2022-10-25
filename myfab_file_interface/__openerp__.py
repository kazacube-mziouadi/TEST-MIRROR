# -*- coding: utf-8 -*-
{
    'name': 'myfab File Interface',
    'version': '1.3.2',
    'author': 'myfab',
    'license': 'Open-prod license',
    'summary': 'Interface myfab pour échanger avec des logiciels externes via fichiers à plat.',
    'category': 'Base',
    'description': """
    Interface myfab pour échanger avec des logiciels externes via fichiers à plat.
    \n\r
    **Aide en ligne :** https://docs.myfab.fr/books/myfab-file-interface
    """,
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
        'myfab_tools',
    ],
    'data': [
        'security/myfab_file_interface_security.xml',
        'security/ir.model.access.csv',
        'views/filters/FilterDatetimeDeltaMF.xml',
        'views/filters/FilterValueComparisonMF.xml',
        'views/setters/MFFieldSetter.xml',
        'views/setters/MFMethodSetter.xml',
        'views/MyFabFileInterfaceWeb.xml',
        'views/wizards/WizardFileInterfaceCronMF.xml',
        'views/wizards/WizardUploadImportFileMF.xml',
        'views/wizards/WizardConfirmImportFileMF.xml',
        'views/model_dictionaries/ModelDictionaryMF.xml',
        'views/model_dictionaries/ModelDictionaryFieldFilterMF.xml',
        'views/model_dictionaries/FileInterfaceExportModelDictionaryMF.xml',
        'views/FileInterfaceMF.xml',
        'views/FileInterfaceExportMF.xml',
        'views/FileInterfaceImportMF.xml',
        'views/files/FileMF.xml',
        'views/files/PhysicalFileMF.xml',
        'views/files/PhysicalDirectoryMF.xml',
        'views/attempts/FileInterfaceAttemptMF.xml',
        'views/attempts/FileInterfaceExportAttemptMF.xml',
        'views/attempts/FileInterfaceImportAttemptMF.xml',
        'views/attempts/RecordImportMF.xml',
        'views/attempts/RecordImportRowMF.xml',
        'views/attempts/FileInterfaceImportAttemptRecordImportMF.xml',
        'views/BaseMenus.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
