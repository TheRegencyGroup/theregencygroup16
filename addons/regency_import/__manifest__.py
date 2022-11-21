{
    'name': 'Regency Import',
    'version': '16.0.0.4',
    'summary': 'Custom fields needed for import of historical data',
    'author': 'OpsWay',
    'description': "",
    'website': '',
    'depends': [
        'regency_contacts',
        'regency_crm',
        'stock_mts_mto_rule',
        'purchase_stock'
    ],
    'data': [
        'data/ir_action_server.xml',
        'security/ir.model.access.csv',
        'views/product_attribute.xml',
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
