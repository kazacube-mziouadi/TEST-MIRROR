# See LICENSE file for full copyright and licensing details.

{
    'name': 'myfab SAV',
    'version': '1.0.0',
    'author': 'myfab',
    'license': 'Open-prod license',
    'depends': [
        'my_fab',
        'sav',
        'myfab_signature'
    ],
    'category': 'Advanced',
    'description': """
        Intègre un champ signature client (signature à main levée) à la fiche d'intervention SAV.
        """,
    'summary': """
        Champ signature client pour fiche SAV
    """,
    'images': [
        'static/description/icon.jpg'
    ],
    'data': [
        'views/Intervention.xml',
    ],
    'website': '',
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
