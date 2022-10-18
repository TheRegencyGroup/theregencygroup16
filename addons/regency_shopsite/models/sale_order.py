from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_with_overlay_ids = fields.One2many('product.image', 'sale_order_line_id', string='Images with overlay')
    overlay_template_id = fields.Many2one('overlay.template', compute='_compute_overlay_template_id')

    @api.depends('product_id', 'product_id.product_template_attribute_value_ids')
    def _compute_overlay_template_id(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        for line in self:
            product_template_attribute_value_ids = line.product_id.product_template_attribute_value_ids
            if overlay_attribute_id.id in product_template_attribute_value_ids.mapped('attribute_id').ids:
                line.overlay_template_id = product_template_attribute_value_ids\
                    .filtered(lambda x: x.attribute_id.id == overlay_attribute_id.id)\
                    .product_attribute_value_id.overlay_template_id.id
            else:
                line.overlay_template_id = False

    def action_open_sale_order_line_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(False, "form")],
        }
