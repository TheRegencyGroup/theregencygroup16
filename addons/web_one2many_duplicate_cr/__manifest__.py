# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': "One2Many Duplicate Records",
    'summary': """One2Many Duplicate Records""",
    'description': """This module helps you to duplicate records in One2many line for Quotation, Sale Order, Invoice etc.""",
    'author': 'Candidroot Solutions Pvt. Ltd, Sergey Chupryna',
    'category': 'Extra Tools',
    'version': '16.0.0.2',  # custom migration
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend':[
            'web_one2many_duplicate_cr/static/src/**/*'
        ]
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'live_test_url': 'https://youtu.be/IjSy-wrtpN0',
    'price': 14.99,
    'currency': 'USD',
    'auto_install': False,
    'application': True,
    'website':'https://www.candidroot.com/'
}
