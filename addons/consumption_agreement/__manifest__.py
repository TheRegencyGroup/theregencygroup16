{
    'name': 'Regency Consumption Agreement',
    'version': '16.0.0.3',
    'summary': '',
    'author': 'OpsWay',
    'description': "",
    'website': '',
    'depends': [
        'sale_management',
        'sale',
        'regency_contacts',
        'purchase_stock',
        'stock_mts_mto_rule'
    ],
    'category': 'Regency',
    'sequence': 3,
    'data': [
        'data/ir_sequence_data.xml',
        'views/sale_order.xml',
        'views/consumption_agreement.xml',
        'views/consumption_agreement_portal.xml',
        'views/sale_order_portal.xml',
        'security/ir.model.access.csv',
        'wizard/create_so_wizard.xml',
        'wizard/sale_make_invoice_advance_views.xml',
        'report/consumption_agreement.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'consumption_agreement/static/src/js/**/*',
            'consumption_agreement/static/src/frontend/js/**/*.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
