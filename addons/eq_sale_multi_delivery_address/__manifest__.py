# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

{
    'name': "Sale Multi Delivery Address",
    'version': '15.0.1.0',
    'category': 'Sales',
    'author': 'Equick ERP',
    'summary': """sale multiple delivery address sale order multiple delivery address for sale multi delivery multi picking sale multi picking sale different delivery address sale multi address sales multi address sale multiple address""",
    'description': """
        This module allow user to select different delivery address on Sales order lines.
        * Generate Delivery orders based on the delivery address selected on order lines.
        * User can see the delivery address on Pdf Report, Customer portal view.
    """,
    'license': 'OPL-1',
    'depends': ['sale_management', 'sale_stock'],
    'price': 14,
    'currency': 'EUR',
    'website': "",
    'data': ['views/sale_view.xml',
             'views/sale_report_template.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: