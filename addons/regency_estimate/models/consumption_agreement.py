from odoo import fields, models


class ConsumptionAgreement(models.Model):
    _inherit = 'consumption.agreement'

    from_pricesheet_id = fields.Many2one('product.price.sheet', help='From what Pricesheet created')
