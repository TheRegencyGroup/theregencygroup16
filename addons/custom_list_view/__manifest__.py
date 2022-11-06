{
    'name': 'Custom List View',
    'version': '16.0.0.0',
    'author': 'OpsWay',
    'license': 'Other proprietary',
    'depends': [
        'web',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_list_view/static/src/list_view/*.js',
            'custom_list_view/static/src/list_view/*.scss',
        ],
    },
    'category': 'Interface',
    'sequence': 5,
    'installable': True,
    'application': False,
    'auto_install': False,
}
