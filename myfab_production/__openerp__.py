# See LICENSE file for full copyright and licensing details.
{
    'name': 'myfab Production',
    'version': '1.0.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'category': 'base',
    'summary': "Intègre des options pour le module de production",
    'description': """
        Intègre des options pour le module de production.
        Attention : pour le paramétrage des heures de saisie par défaut, le fuseau horaire de l'utilisateur dans 
        Open-Prod doit être le même que celui de son navigateur Internet.
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
