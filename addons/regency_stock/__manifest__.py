{
    'name': 'Regency Stock',
    'version': '16.0.0.1',
    'summary': '',
    'author': 'OpsWay',
    'description': "",
    'depends': [
        'delivery'
    ],
    'category': 'Regency/Stock',
    'sequence': 10,
    'data': [
        'report/stock_report_views.xml',
        'report/report_package_barcode.xml',
        'wizard/choose_receipt_package_views.xml',
        'views/stock_quant_package.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
