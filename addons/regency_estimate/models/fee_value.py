from odoo import fields, models, api, _
from odoo.exceptions import UserError


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
    price_sheet_line_id = fields.Many2one('product.price.sheet.line', copy=False)
    purchase_requisition_line_id = fields.Many2one('purchase.requisition.line', copy=False)
    po_line_id = fields.Many2one('purchase.order.line', copy=False)
    portal_value = fields.Float(compute='_compute_portal_value', store=True)
    per_item = fields.Boolean()

    @api.depends('price_sheet_line_id.product_uom_qty', 'value', 'percent_value', 'price_sheet_line_id.min_quantity')
    def _compute_portal_value(self):
        for rec in self:
            if rec.price_sheet_line_id.product_uom_qty > 0:
                if not rec.percent_value:
                    rec.portal_value = rec.value
                else:
                    rec.portal_value = rec.price_sheet_line_id.price * rec.price_sheet_line_id.product_uom_qty * rec.percent_value / 100
            else:
                rec.portal_value = 0

    @api.onchange('percent_value')
    def _onchange_percent_value(self):
        self.value = self.price_sheet_line_id.price * self.price_sheet_line_id.min_quantity * self.percent_value / 100 \
                     or self.purchase_requisition_line_id.price_unit * self.purchase_requisition_line_id.product_qty * self.percent_value / 100 \
                     or self.po_line_id.price_unit * self.po_line_id.product_qty * self.percent_value / 100

    @api.onchange('per_item')
    def _onchange_per_item(self):
        self.percent_value = 0 if self.per_item else self.percent_value
