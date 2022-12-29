from odoo import fields, models, api


class FeeValue(models.Model):
    _name = 'fee.value'
    _description = 'Fee Value'
    _sql_constraints = [
        ('check_line_specific',
         '''CHECK((po_line_id is null and purchase_requisition_line_id is null and price_sheet_line_id is not null)
          or (po_line_id is not null and purchase_requisition_line_id is null and price_sheet_line_id is null)
           or (po_line_id is null and purchase_requisition_line_id is not null and price_sheet_line_id is null))''',
         'Only one of three line_id fields should have value.')
    ]

    fee_type_id = fields.Many2one('fee.type', required=True)
    value = fields.Float(required=True)
    percent_value = fields.Float()
    price_sheet_line_id = fields.Many2one('product.price.sheet.line')
    purchase_requisition_line_id = fields.Many2one('purchase.requisition.line')
    po_line_id = fields.Many2one('purchase.order.line')
    portal_value = fields.Float(compute='_compute_portal_value', store=True)
    per_item = fields.Boolean()

    @api.depends('price_sheet_line_id.product_uom_qty', 'value', 'percent_value', 'price_sheet_line_id.min_quantity',
                 'per_item')
    def _compute_portal_value(self):
        for rec in self:
            rec.portal_value = 100  # rec.get_fee_sum(rec.price_sheet_line_id.product_uom_qty, rec.price_sheet_line_id.price)

    def get_fee_sum(self, qty, price):
        fee_sum = 0
        for fee in self:
            if fee.per_item:
                fee_sum += qty * fee.value
            elif fee.percent_value:
                fee.value = qty * price * fee.percent_value / 100
                fee_sum += fee.value
            else:
                fee_sum += fee.value
        return fee_sum

    @api.onchange('percent_value')
    def _onchange_percent_value(self):
        self.value = self.price_sheet_line_id.price * self.price_sheet_line_id.min_quantity * self.percent_value / 100 \
                     or self.purchase_requisition_line_id.price_unit * self.purchase_requisition_line_id.product_qty * self.percent_value / 100 \
                     or self.po_line_id.price_unit * self.po_line_id.product_qty * self.percent_value / 100

    @api.onchange('per_item')
    def _onchange_per_item(self):
        self.percent_value = 0 if self.per_item else self.percent_value
