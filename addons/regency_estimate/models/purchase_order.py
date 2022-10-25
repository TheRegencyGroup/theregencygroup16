from odoo import fields, models, api, Command
from odoo.tools import get_lang
from odoo.addons.purchase_requisition.models.purchase import PurchaseOrderLine


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

class MyPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _new_compute_price_unit_and_date_planned_and_name(self):
        """Override for fixing bugs"""
        po_lines_without_requisition = self.env['purchase.order.line']
        for pol in self:
            if pol.product_id.id not in pol.order_id.requisition_id.line_ids.product_id.ids:
                po_lines_without_requisition |= pol
                continue
            for line in pol.order_id.requisition_id.line_ids:
                if line.product_id == pol.product_id:
                    pol.price_unit = line.product_uom_id._compute_price(line.price_unit, pol.product_uom)
                    partner = pol.order_id.partner_id or pol.order_id.requisition_id.vendor_id
                    product_ctx = {'seller_id': partner.id, 'lang': get_lang(pol.env, partner.lang).code}
                    name = pol._get_product_purchase_description(pol.product_id.with_context(product_ctx))
                    if line.product_description_variants:
                        name += '\n' + line.product_description_variants
                    pol.name = name
                    break
        super(PurchaseOrderLine, po_lines_without_requisition)._compute_price_unit_and_date_planned_and_name()


PurchaseOrderLine._compute_price_unit_and_date_planned_and_name = MyPurchaseOrderLine._new_compute_price_unit_and_date_planned_and_name

