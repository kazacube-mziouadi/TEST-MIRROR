# -*- coding: utf-8 -*-
{
    'name': 'MyFab File Interface',
    'version': '1.0.0',
    'author': 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Interface MyFab pour échanger avec des logiciels externes via fichiers à plat.',
    'category': 'Base',
    'description': """Interface MyFab pour échanger avec des logiciels externes via fichiers à plat.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
        'base_openprod',
        'base',
        'web_kanban',
        'web_calendar',
        'auth_crypt',
        'decimal_precision',
        'web_tip',
        'maintenance_contract',
        'web_tree_field_color',
        'web_diagram',
        'mail',
        'web_view_editor',
        'web_editor',
        'web_to_upper',
        'web_float_time_seconds',
        'web_expression_builder',
        'web_char_trim',
        'favorite',
        'document',
        'web_highstock',
        'base_import',
        'web_kanban_gauge',
        'binary_attachment',
        'report',
        'web_openprod',
        'purchase',
        'delivery_address',
        'web_data_base_name',
        'auth_signup',
        'compute_stored_fields',
        'calendar',
        'charge',
        'analytic',
        'l10n_fr',
        'account_openprod',
        'base_iban',
        'data_base_report',
        'data_account_report',
        'edi_openprod',
        'mass_editing',
        'stock_location',
        'excel_import',
        'web_export_view',
        'mrp',
        'account',
        'warning',
        'account_voucher',
        'base_printers',
        'printers',
        'printers_mrp',
        'printers_stock',
        'printers_res_partner',
        'printers_resource',
        'workflow_initialization',
        'jasper_server',
        'workflow_migration',
        'account_chart',
        'web_modify_view',
        'web_view_field_list',
        'base_setup',
        'partner_openprod',
        'product',
        'excel_report',
        'fetchmail',
        'base_action_rule',
        'workflow_reinitialisation',
        'enterprise_social_network',
        'resource',
        'export_security',
        'web_field_selector',
        'stock',
        'board',
        'translator',
        'function_fields_translation',
        'sale',
        'sale_purchase',
        'web_verify_mail',
        'base_vat',
        'web_charts',
        'web',
        'web_mail_autocomplete'
    ],
    'data': [
        'security/myfab_file_interface_security.xml',
        'security/ir.model.access.csv',
        'views/filters/FilterDatetimeDeltaMF.xml',
        'views/filters/FilterValueComparisonMF.xml',
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
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'not_show': True
}
