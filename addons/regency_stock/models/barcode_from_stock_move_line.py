from odoo import models, fields


class BarcodeReport(models.TransientModel):
    _name = 'barcode.report'

    package_name = fields.Char()
    company = fields.Many2one('res.company')
    qty_done = fields.Integer()
    customer_name = fields.Char()
    product_name = fields.Char()
