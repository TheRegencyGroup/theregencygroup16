from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_values(self, product_id, quantity, linked_line_id=False, no_variant_attribute_values=None,
                                   product_custom_attribute_values=None, **kwargs):
        result = super()._prepare_order_line_values(product_id, quantity, linked_line_id, no_variant_attribute_values,
                                                    product_custom_attribute_values, **kwargs)
        if 'delivery_partner_id' in kwargs:
            result['delivery_partner_id'] = kwargs['delivery_partner_id']
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_with_overlay_ids = fields.One2many('product.image', 'sale_order_line_id', string='Images with overlay')
    overlay_template_id = fields.Many2one('overlay.template', compute='_compute_overlay_template_id')

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        res._link_overlay_to_product()
        return res

    def _link_overlay_to_product(self):
        for line in self:
            attribute_ids = line.product_template_attribute_value_ids.mapped('attribute_id')
            if self.env.ref('regency_shopsite.overlay_attribute') in attribute_ids and self.env.ref(
                    'regency_shopsite.customization_attribute') in attribute_ids:
                for overlay_product in line.product_template_id.overlay_template_ids.mapped('overlay_product_ids'):
                    overlay_product.product_id = line.product_id.id

    @api.depends('product_id', 'product_id.product_template_attribute_value_ids')
    def _compute_overlay_template_id(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        for line in self:
            product_template_attribute_value_ids = line.product_id.product_template_attribute_value_ids
            if overlay_attribute_id.id in product_template_attribute_value_ids.mapped('attribute_id').ids:
                line.overlay_template_id = product_template_attribute_value_ids \
                    .filtered(lambda x: x.attribute_id.id == overlay_attribute_id.id) \
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
