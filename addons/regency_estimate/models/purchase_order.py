from odoo import fields, models, api, Command


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[
        ('confirmed_prices', 'Confirmed prices'),
    ], ondelete={
        'confirmed_prices': lambda recs: recs.write({'state': 'draft'}),
    })

    def action_confirm_prices(self):
        self.write({'state': 'confirmed_prices'})
        for rec in self.filtered(lambda l: l.requisition_id):
            for line in rec.order_line:
                req_line = rec.requisition_id.line_ids.filtered(lambda l: l.product_id == line.product_id
                                                                      and (l.partner_id == rec.partner_id or not l.partner_id)
                                                                      and l.product_qty == line.product_qty)
                if req_line:
                    req_line.write({'partner_id': rec.partner_id.id,
                                    'price_unit': line.price_unit,
                                    'product_qty': line.product_qty})
                else:
                    self.env['purchase.requisition.line'].create({
                        'requisition_id': rec.requisition_id.id,
                        'product_description_variants': line.name,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'price_unit': line.price_unit,
                        'partner_id': rec.partner_id.id,
                        'product_uom_id': line.product_uom.id
                    })
