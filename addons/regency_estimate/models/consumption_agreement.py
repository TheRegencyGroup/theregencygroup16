from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'consumption.agreement'

    price_sheet_id = fields.Many2one('product.price.sheet')

