from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.template'

    sale_order_line_ids = fields.One2many('sale.order.line', 'product_template_id')
    sale_order_ids = fields.Many2many('sale.order', compute='_compute_sale_order_ids', store=True)
    last_order_date = fields.Date(compute='_compute_last_order')
    last_order_qty = fields.Float(compute='_compute_last_order')
    last_order_uom_id = fields.Many2one('uom.uom', compute='_compute_last_order')
    last_vendor_ids = fields.One2many('res.partner', compute='_compute_last_order')
    customer_ids = fields.Many2many('res.partner', 'customer_product_rel', compute='_compute_customer_ids', store=True,
                                    index=True)

    @api.depends('sale_order_line_ids')
    def _compute_customer_ids(self):
        for rec in self:
            rec.customer_ids = self.env['sale.order.line'].search([('product_template_id', '=', rec.id)]).filtered(
                lambda f: f.order_id.state in ['sale', 'done']).mapped('order_partner_id')

    @api.depends('sale_order_ids')
    def _compute_last_order(self):
        for rec in self:
            last_order = rec.sale_order_ids.sorted('date_order', reverse=True)
            if last_order:
                last_order = last_order[0]
            rec.last_order_date = last_order.date_order
            rec.last_order_qty = sum(
                last_order.order_line.filtered(lambda f: f.product_template_id == rec).mapped('product_uom_qty'))
            rec.last_vendor_ids = last_order.order_line.filtered(lambda f: f.product_template_id == rec).mapped(
                'purchase_line_ids').mapped('partner_id')
            rec.last_order_uom_id = last_order.order_line.filtered(lambda f: f.product_template_id == rec).mapped(
                'product_uom')

    @api.depends('sale_order_line_ids')
    def _compute_sale_order_ids(self):
        for rec in self:
            rec.sale_order_ids = self.env['sale.order.line'].search([('product_template_id', '=', rec.id)]).filtered(
                lambda f: f.order_id.state in ['sale', 'done']).mapped('order_id')
