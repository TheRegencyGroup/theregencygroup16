from odoo import fields, models, api, _


class FeeValue(models.Model):
    _name = 'fee.value'
    _description = 'Create additional fees for price sheet line'

    name = fields.Char(required=True)
    fee_type_id = fields.Many2one('fee.type', required=True)
    value = fields.Float(required=True)
    percent_value = fields.Float()
    price_sheet_line_id = fields.Many2one('product.price.sheet.line', required=True)
    portal_value = fields.Float(compute='_compute_portal_value', store=True, required=True)

    @api.depends('price_sheet_line_id.product_uom_qty', 'value', 'percent_value', 'price_sheet_line_id.min_quantity')
    def _compute_portal_value(self):
        for rec in self:
            if rec.price_sheet_line_id.product_uom_qty > 0:
                if not rec.percent_value:
                    rec.portal_value = rec.value
                else:
                    rec.portal_value = rec.value / rec.price_sheet_line_id.min_quantity * rec.price_sheet_line_id.product_uom_qty
            else:
                rec.portal_value = 0

    @api.onchange('percent_value')
    def _onchange_percent_value(self):
        self.value = self.price_sheet_line_id.price * self.price_sheet_line_id.min_quantity * self.percent_value / 100
