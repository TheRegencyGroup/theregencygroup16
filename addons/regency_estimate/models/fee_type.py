from odoo import fields, models


class FeeType(models.Model):
    _name = 'fee.type'
    _description = 'Set additional fee types for setting additional fee values for price sheet lines'

    name = fields.Char(required=True)
    product_id = fields.Many2one('product.product', domain="[('detailed_type', '=', 'service')]", required=True)
