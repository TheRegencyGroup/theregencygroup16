{
    'name': 'Regency Import',
    'version': '16.0.0.3',
    'summary': 'Custom fields needed for import of historical data',
    'author': 'OpsWay',
    'description': "",
    'website': '',
    'depends': [
        'regency_contacts',
        'regency_crm'
    ],
    'data': [
        'data/ir_action_server.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/res_country.xml'
    ],
    'category': 'Regency',
    'sequence': 5,
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
