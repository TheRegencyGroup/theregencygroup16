# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Select Multiple Product Images Omax',
    'author': 'Omax Informatics',
    'version' : '15.0.1',
    'website': 'https://www.omaxinformatics.com',
    'category': 'webiste',
    'description': 'The Module help to upload multiple product images at single time.',
    'summary': """
        Select Multiple images in single time.
        upload more than one image at once.
        Remove all extra images at once.
        delete all images in single time.
        upload extra product images for ecommerce product at single time.
        delete extra product images for ecommerce product at once.
        Easy to add multiple product images for ecommerce at once.
    """,
    'depends' : ['web','website_sale'],
    'data': [
        "views/view.xml",
    ],
    "images": ["static/description/banner.jpg",],
    'license': 'AGPL-3',
    'currency':'USD',
    'price': 40.0,
    'pre_init_hook': 'pre_init_check',
    'assets': {
        'web.assets_backend': [
            'product_multiple_images/static/src/css/product_multiple_images.css',
            'product_multiple_images/static/src/js/product_multiple_images.js',
        ],
        'web.assets_qweb': [
            'product_multiple_images/static/src/xml/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
