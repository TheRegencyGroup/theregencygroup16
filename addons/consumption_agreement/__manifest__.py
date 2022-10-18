{
    'name': 'Regency Consumption Agreement',
    'version': '15.0.0.3',
    'summary': '',
    'author': 'OpsWay',
    'description': "",
    'website': '',
    'depends': [
        'sale_management',
        'sale',
        'regency_contacts'
    ],
    'category': 'Regency',
    'sequence': 3,
    'data': [
        'data/ir_sequence_data.xml',
        'views/sale_order.xml',
        'views/consumption_agreement.xml',
        'views/consumption_agreement_portal.xml',
        'views/sale_order_portal.xml',
        'security/ir.model.access.csv'
    ],
    'assets': {
        'web.assets_frontend': [
            'consumption_agreement/static/src/js/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
