from odoo import fields, models, api, _


class FeeValue(models.Model):
    _name = 'fee.value'

    name = fields.Char()
    fee_type_id = fields.Many2one('fee.type')
    value = fields.Float()
    percent_value = fields.Float()
    price_sheet_line_id = fields.Many2one('product.price.sheet.line')

    @api.onchange('percent_value')
    def _onchange_percent_value(self):
        self.value = self.price_sheet_line_id.price * self.price_sheet_line_id.min_quantity * self.percent_value / 100
