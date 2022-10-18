{
    'name': 'Regency Hotel Template relation',
    'version': '15.0.0.0',
    'summary': '',
    'author': 'OpsWay',
    'description': "",
    'depends': [
        'regency_contacts',
        'regency_shopsite',
        'sale'
    ],
    'category': 'Regency',
    'sequence': 10,
    'data': [
        'views/overlay_template_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
