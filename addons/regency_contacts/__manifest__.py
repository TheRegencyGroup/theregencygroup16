{
    'name': 'Regency Contacts',
    'version': '16.0.0.1',
    'summary': '',
    'author': 'OpsWay',
    'description': "",
    'depends': [
        'contacts'
    ],
    'category': 'Regency/Contacts',
    'sequence': 10,
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'data/association_type.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
