{
    'name': 'Regency Stock Picking Batch',
    'version': '16.0.0.1',
    'author': 'OpsWay',
    'license': "Other proprietary",
    'depends': [
        'stock_picking_batch',
        'sale',
        'stock_landed_costs',
        'regency_estimate'
    ],
    'data': [
        'views/stock_picking_batch_views.xml',
        'views/stock_landed_costs.xml',
        'views/sale_estimate.xml'
    ],
    'category': 'Regency',
    'sequence': 5,
    'installable': True,
    'application': True,
    'auto_install': False,
}
