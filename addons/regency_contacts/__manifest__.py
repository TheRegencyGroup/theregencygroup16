{
    'name': 'Regency Contacts',
    'version': '16.0.1.2',
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
        'views/customer_association.xml',
        'data/association_type.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'regency_contacts/static/src/*/**.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
