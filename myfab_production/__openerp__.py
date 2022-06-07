# See LICENSE file for full copyright and licensing details.
{
    'name': 'myfab Production',
    'version': '1.0.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'category': 'base',
    'description': """
        Intègre des options pour le module de production 
    """,
    'summary': """
        Intègre des options pour le module de production
    """,
    'images': [],
    'depends': [
        'purchase',
    ],
    'data': [
        'data/MFProductionConfig.xml',
        'views/MFProductionConfig.xml',
        'views/BaseMenus.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'not_show': True,
}
