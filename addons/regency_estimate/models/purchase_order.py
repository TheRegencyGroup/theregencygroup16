from odoo import fields, models, api
from odoo.tools import get_lang
from odoo.addons.purchase_requisition.models.purchase import PurchaseOrderLine


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[
        ('confirmed_prices', 'Confirmed prices'),
    ], ondelete={
        'confirmed_prices': lambda recs: recs.write({'state': 'draft'}),
    })
    show_column_produced_overseas = fields.Boolean(compute='_compute_show_column_produced_overseas')
    tracking_ref = fields.Char(compute='_compute_tracking_references')
    cancellation_reason = fields.Char()

    def _compute_tracking_references(self):
        for entry in self:
            if entry.picking_ids:
                entry.tracking_ref = " ,".join(ref for ref in entry.picking_ids.mapped('carrier_tracking_ref') if ref)
            else:
                entry.tracking_ref = False

    @api.depends('partner_id', 'partner_id.is_company', 'partner_id.contact_type', 'partner_id.vendor_type')
    def _compute_show_column_produced_overseas(self):
        for rec in self:
            rec.show_column_produced_overseas = rec.partner_id.is_company \
                                                and rec.partner_id.contact_type == 'vendor' \
                                                and rec.partner_id.vendor_type == 'overseas'

    @api.onchange('partner_id')
    @api.depends('partner_id', 'partner_id.is_company', 'partner_id.contact_type', 'partner_id.vendor_type')
    def _onchange_partner_id(self):
        if self.partner_id.is_company \
                and self.partner_id.contact_type == 'vendor' \
                and self.partner_id.vendor_type == 'overseas':
            self.order_line.write({'produced_overseas': True})
        else:
            self.order_line.write({'produced_overseas': False})

    def action_confirm_prices(self):
        self.write({'state': 'confirmed_prices'})
        for rec in self.filtered(lambda f: f.requisition_id):
            for line in rec.order_line:
                req_line = rec.requisition_id.line_ids.filtered(lambda f: f.product_id == line.product_id
                                                                          and (
                                                                                  f.partner_id == rec.partner_id or not f.partner_id)
                                                                          and f.product_qty == line.product_qty)
                if req_line:
                    req_line.write({'partner_id': rec.partner_id.id,
                                    'price_unit': line.price_unit,
                                    'product_qty': line.product_qty,
                                    'produced_overseas': line.produced_overseas})
                else:
                    self.env['purchase.requisition.line'].create({
                        'requisition_id': rec.requisition_id.id,
                        'product_description_variants': line.name,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'price_unit': line.price_unit,
                        'partner_id': rec.partner_id.id,
                        'product_uom_id': line.product_uom.id,
                        'produced_overseas': line.produced_overseas,
                    })

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['invoice_date'] = fields.Datetime.now()
        return invoice_vals

    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        self.ensure_one()
        value = self.env['purchase.order.cancel.wizard'].sudo().create({'cancellation_reason': ''})
        if self.state == 'purchase':
            return {
                'name': 'Cancel',
                'view_mode': 'form',
                'res_model': 'purchase.order.cancel.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': value.id
            }
        return res


class MyPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    produced_overseas = fields.Boolean(string='Produced overseas')
    customer_id = fields.Many2one('res.partner')

    @api.onchange('product_id')
    def onchange_product_id(self):
        super().onchange_product_id()
        self.produced_overseas = self.partner_id.is_company \
                                 and self.partner_id.contact_type == 'vendor' \
                                 and self.partner_id.vendor_type == 'overseas'

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

    @api.model
    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, company_id, values,
                                                      po):
        res = super()._prepare_purchase_order_line_from_procurement(product_id, product_qty, product_uom, company_id,
                                                                    values, po)
        if values['pricesheet_vendor_id']:
            res.update({'price_unit': values['pricesheet_vendor_price']})
        if values['customer_id']:
            res.update({'customer_id': values['customer_id']})
        return res


PurchaseOrderLine._compute_price_unit_and_date_planned_and_name = MyPurchaseOrderLine._new_compute_price_unit_and_date_planned_and_name
