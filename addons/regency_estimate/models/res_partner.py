from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_estimate_ids = fields.One2many('sale.estimate', 'partner_id')
    sale_estimate_count = fields.Integer(compute='_compute_estimate_count')

    product_pricesheet_ids = fields.One2many('product.price.sheet', 'partner_id')
    product_pricesheet_count = fields.Integer(compute='_compute_pricesheet_count')

    rfq_ids = fields.One2many('sale.order', 'partner_id', domain=[('state', '=', 'draft')])
    rfq_count = fields.Integer(compute='_compute_rfq_count')

    consumption_agreement_ids = fields.One2many('consumption.agreement', 'partner_id')
    consumption_agreement_count = fields.Integer(compute='_compute_consumption_agreement_count')

    purchase_order_ids = fields.One2many('purchase.order', 'partner_id')
    purchase_order_line_ids = fields.One2many('purchase.order.line', 'partner_id')
    product_count = fields.Integer(compute='_compute_product_product_count')

    def _compute_estimate_count(self):
        for rec in self:
            rec.sale_estimate_count = len(rec.sale_estimate_ids)

    def action_show_sale_estimates(self):
        action = self.env["ir.actions.actions"]._for_xml_id("regency_estimate.sale_estimate_all")
        action['domain'] = [('id', 'in', self.sale_estimate_ids.ids)]
        return action

    def _compute_pricesheet_count(self):
        for rec in self:
            rec.product_pricesheet_count = len(rec.product_pricesheet_ids)

    def action_show_product_pricesheets(self):
        action = self.env["ir.actions.actions"]._for_xml_id("regency_estimate.action_product_price_sheet")
        action['domain'] = [('id', 'in', self.product_pricesheet_ids.ids)]
        return action

    def _compute_rfq_count(self):
        for rec in self:
            rec.rfq_count = len(rec.rfq_ids)

    def action_show_rfq(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations")
        action['domain'] = [('id', 'in', self.rfq_ids.ids)]
        return action

    def _compute_consumption_agreement_count(self):
        for rec in self:
            rec.consumption_agreement_count = len(rec.consumption_agreement_ids)

    def action_show_consumption_agreements(self):
        action = self.env["ir.actions.actions"]._for_xml_id("consumption_agreement.consumption_agreement_action")
        action['domain'] = [('id', 'in', self.consumption_agreement_ids.ids)]
        return action

    def _compute_product_product_count(self):
        for rec in self:
            product_ids = rec.purchase_order_ids.filtered(
                lambda product: product.invoice_status == 'invoiced' and product.receipt_status == 'full').mapped('product_id')
            rec.product_count = len(product_ids)

    def action_show_products(self):
        product_ids = self.purchase_order_ids.filtered(
            lambda product: product.invoice_status == 'invoiced' and product.receipt_status == 'full').mapped(
            'product_id')
        action = self.env["ir.actions.actions"]._for_xml_id('regency_estimate.product_action_partner')
        action['domain'] = [('id', 'in', product_ids.ids)]
        action['views'] = action['views'][:-1]
        # a = 3
        return action

