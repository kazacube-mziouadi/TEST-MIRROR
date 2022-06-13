# See LICENSE file for full copyright and licensing details.

{
    'name': 'myfab Signature',
    'version': '1.1.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'depends': [
        'my_fab',
        'sav'
    ],
    'category': 'advanced',
    'description': """
        Permet également de créer un champ signature sur n'importe quel modèle (sur l'exemple du SAV). 
    """,
    'summary': """
        Création d'un  champ signature sur n'importe qu'elle modèle
    """,
    'images': [
        'static/description/icon.jpg'
    ],
    'data': [
        'views/web_digital_sign_view.xml',
        'wizards/mf_create_signature/mf_create_signature.xml',
    ],
    'website': '',
    'qweb': [
        'static/src/xml/digital_sign.xml'
    ],
    'installable': True,
    'auto_install': False,
}
