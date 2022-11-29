{
    'name': 'Regency Backend Interface',
    'version': '16.0.0.1',
    'author': 'OpsWay',
    'license': 'Other proprietary',
    'depends': [
        'web',
    ],
    'assets': {
        'web.assets_backend': [
            'regency_backend_interface/static/src/scss/*.scss',
            'regency_backend_interface/static/src/views/**/*.js',
            'regency_backend_interface/static/src/views/**/*.xml',
            'regency_backend_interface/static/src/views/**/*.scss',
        ],
    },
    'category': 'Interface',
    'sequence': 5,
    'installable': True,
    'application': False,
    'auto_install': False,
}
