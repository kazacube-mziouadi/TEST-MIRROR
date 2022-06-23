# See LICENSE file for full copyright and licensing details.

{
    'name': 'myfab Signature',
    'version': '2.0.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'depends': [
        'my_fab'
    ],
    'category': 'advanced',
    'description': """
        Permet de créer un champ signature sur n'importe quel modèle. 
    """,
    'summary': """
        Création d'un champ signature sur n'importe quel modèle
    """,
    'images': [
        'static/description/icon.jpg'
    ],
    'data': [
        'views/web_digital_sign_view.xml',
        'views/MFSignatureConfig.xml',
        'views/BaseMenus.xml',
    ],
    'website': '',
    'qweb': [
        'static/src/xml/digital_sign.xml'
    ],
    'installable': True,
    'auto_install': False,
}
