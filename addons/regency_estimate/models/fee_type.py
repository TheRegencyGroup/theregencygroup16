from odoo import fields, models


class FeeType(models.Model):
    _name = 'fee.type'

    name = fields.Char()
    product_id = fields.Many2one('product.product', domain="[('detailed_type', '=', 'service')]")
