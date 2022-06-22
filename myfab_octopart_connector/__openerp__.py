# -*- coding: utf-8 -*-
{
    'name' : 'Connecteur Octopart',
    'version' : '1.0.0',
    'author' : 'myfab',
    'license': 'Open-prod license',
    'summary': 'Connecteur Octopart par myfab',
    'category' : 'Product',
    'description' : """
        Connecteur OCTOPART importation produit électronique
    """,
    'website': 'https://www.myfab.fr/',
    'module_type': 'optional',
    'depends' : [
        'my_fab',
        'product', 
        'partner_openprod', 
        'purchase', 
        'characteristics',
    ],
    'data': [
            'security/import_product_connector_security.xml',
            'security/ir.model.access.csv',
            'views/technical_data_config.xml',
            'views/octopart_menu.xml',
            'views/octopart_manufacturer.xml',
            'views/octopart_seller.xml',
            'views/octopart_category.xml',
            'wizard/data/import_manufacturer.xml',
            'wizard/data/import_seller.xml',
            'wizard/data/import_category.xml',
            'wizard/data/import_characteristics.xml',
            'wizard/advanced_search/advanced_search.xml',
            'wizard/import_product/octopart_import_product.xml',
            'wizard/seller_connect/add_octopart_id.xml',
            'wizard/prices/add_octopart_price.xml',
            'views/octopart_product_search.xml',
            'views/partner.xml',
            'views/product.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
