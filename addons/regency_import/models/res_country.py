from odoo import fields, models, api, _, tools


class Country(models.Model):
    _inherit = 'res.country'

    alternative_name = fields.Char()


class Country(models.Model):
    _inherit = 'res.country.state'

    alternative_code = fields.Char()

