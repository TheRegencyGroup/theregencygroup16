from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.template'

    sale_order_line_ids = fields.One2many('sale.order.line', 'product_template_id')
    sale_order_ids = fields.Many2many('sale.order', compute='_compute_sale_order_ids', store=True)
    # sale_order_dates = fields.Char(compute='_compute_sale_order_dates')
    # vendor_ids = fields.One2many(compute='_compute_vendor_ids')
    customer_ids = fields.Many2many('res.partner', 'customer_product_rel', compute='_compute_customer_ids', store=True,
                                    index=True)

    @api.depends('sale_order_ids')
    def _compute_customer_ids(self):
        for rec in self:
            rec.customer_ids = rec.sale_order_ids.mapped('partner_id')

    # def _compute_sale_order_dates(self):
    #     for rec in self:
    #         rec.sale_order_dates = ', '.join(fields.Datetime.to_string(x) for x in rec.sale_order_ids.mapped('date_order'))

    @api.depends('sale_order_line_ids')
    def _compute_sale_order_ids(self):
        for rec in self:
            rec.sale_order_ids = self.env['sale.order.line'].search([('product_template_id', '=', rec.id)]).filtered(
                lambda f: f.order_id.state in ['sale', 'done']).mapped('order_id')
