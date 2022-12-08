{
    'name': 'Product Multiple Images Upload',
    'author': 'Opsway',
    'version': '16.0.0.0',
    'website': 'https://www.opsway.com',
    'category': 'Sales',
    'description': 'Product Multiple Images Upload',
    'summary': """
        Product Multiple Images Upload
    """,
    'depends': [
        'web',
        'website_sale',
    ],
    'data': [
        'views/view.xml',
    ],
    'images': [],
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'product_multiple_images_upload/static/src/*.js',
            'product_multiple_images_upload/static/src/*.scss',
            'product_multiple_images_upload/static/src/*.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
