# -*- coding: utf-8 -*-
{
    'name' : 'MyFab Base',
    'version': '0.1.0',
    'author': 'MyFab',
    'license': 'Open-prod license',
    'summary': 'Initialisation modules et données pour MyFab',
    'category': 'Base',
    'description': """Initialise les modules et données statiques nécessaires à une installation standard.""",
    'website': 'https://www.myfab.fr/',
    'module_type': 'base',
    'images': [],
    'depends': [
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
        'classes/InstallerTriggerMF.yml',
        'views/my_fab_web.xml'
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
