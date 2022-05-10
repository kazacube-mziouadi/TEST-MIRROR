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
        Intègre un champ signature client (signature à main levée) à la fiche d'intervention SAV.
        Permet également de créer un champ signature sur n'importe quel modèle (sur l'exemple du SAV). 
    """,
    'summary': """
        Champ signature client pour fiche SAV
    """,
    'images': [
        'static/description/icon.jpg'
    ],
    'data': [
        'views/web_digital_sign_view.xml',
        'views/Intervention.xml'
    ],
    'website': 'http://www.serpentcs.com',
    'qweb': [
        'static/src/xml/digital_sign.xml'
    ],
    'installable': True,
    'auto_install': False,
}
