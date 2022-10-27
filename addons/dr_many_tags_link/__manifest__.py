# -*- coding: utf-8 -*-
{
    'name': "2Many Tags Link",

    'summary': """
        Allow you to directly click on many2many tags in forms to open the associated models.
    """,

    'description': """
        Allow you to directly click on many2many tags in forms to open the associated models.\n
        If you need the original color picker function for tags, press Shift while clicking.
    """,

    'author': "DevReaction",
    'license': 'OPL-1',
    'website': "https://www.devreaction.com",
    'maintainer': 'DevReaction',
    #'live_test_url': 'https://test-odoo.devreaction.com',
    'category': 'Extra Tools',
    'version': '16.0.0.1',
    'support': 'contact@devreaction.com',
    'images': ['static/description/banner.gif'],
    'assets': {
            'web.assets_backend': [
                'dr_many_tags_link/static/src/js/*.js',
                'dr_many_tags_link/static/src/js/*.xml',
            ],
        },

    'depends': ['base', 'web']

}
