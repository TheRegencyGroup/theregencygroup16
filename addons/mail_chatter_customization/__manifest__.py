{
    'name': 'Mail Chatter Customization',
    'version': '16.0.0.0',
    'author': 'OpsWay',
    'license': 'Other proprietary',
    'depends': [
        'mail',
    ],
    'assets': {
        'web.assets_backend': [
            'mail_chatter_customization/static/src/form_view/*.js',
            'mail_chatter_customization/static/src/form_view/*.scss',
        ],
    },
    'category': 'Interface',
    'sequence': 5,
    'installable': True,
    'application': False,
    'auto_install': False,
}
