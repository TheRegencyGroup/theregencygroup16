from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    overlay_product_id = fields.Many2one('overlay.product', compute='_compute_overlay_product_id')

    @api.depends('product_template_attribute_value_ids')
    def _compute_overlay_product_id(self):
        overlay_customize_id = self.env.ref('regency_shopsite.customization_attribute')
        for rec in self:
            product_template_attribute_value_ids = rec.product_template_attribute_value_ids
            if overlay_customize_id.id in product_template_attribute_value_ids.mapped('attribute_id').ids:
                rec.overlay_product_id = product_template_attribute_value_ids \
                    .filtered(lambda x: x.attribute_id.id == overlay_customize_id.id) \
                    .product_attribute_value_id.overlay_product_id.id
            else:
                rec.overlay_product_id = False

    @property
    def url(self):
        overlay_product = self.overlay_product_id
        return overlay_product.url if overlay_product else self.website_url

    def open_pricelist_rules(self):
        self.ensure_one()
        domain = ['|',
                  '&', ('product_tmpl_id', '=', self.product_tmpl_id.id), ('applied_on', '=', '1_product'),
                  '&', ('product_id', '=', self.id), ('applied_on', '=', '0_product_variant'),
                  '&', ('overlay_tmpl_id', '=', self.product_tmpl_id.overlay_tmpl_id.id), ('applied_on', '=', '4_overlay_template')]
        return {
            'name': 'Price Rules',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('product.product_pricelist_item_tree_view_from_product').id, 'tree'), (False, 'form')],
            'res_model': 'product.pricelist.item',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            'context': {
                'default_product_id': self.id,
                'default_applied_on': '0_product_variant',
            }
        }
