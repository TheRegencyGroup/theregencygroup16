import json

from markupsafe import Markup
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_fit_for_overlay = fields.Boolean(string='Can be used for Shopsite', default=False)
    overlay_template_count = fields.Integer(compute='_compute_overlay_template_count')
    overlay_template_ids = fields.One2many('overlay.template', 'product_template_id')

    @api.constrains('attribute_line_ids', 'is_fit_for_overlay')
    def _constrains_attribute_line_ids(self):
        color_attribute_id = self.env.ref('regency_shopsite.color_attribute')
        for rec in self:
            if rec.is_fit_for_overlay and color_attribute_id.id not in rec.attribute_line_ids.mapped('attribute_id').ids:
                raise UserError('Product for overlay template must have color attribute')

    def _compute_overlay_template_count(self):
        for rec in self:
            rec.overlay_template_count = len(rec.overlay_template_ids)

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        return res

    def open_pricelist_rules(self):
        """
        overridden to get price rules set on overlay template
        """
        self.ensure_one()
        domain = ['|', '|',
                  ('product_tmpl_id', '=', self.id),
                  ('product_id', 'in', self.product_variant_ids.ids),
                  # start custom logic
                  ('overlay_tmpl_id', 'in', self.overlay_template_ids.ids)]
                  # end custom logic
        return {
            'name': _('Price Rules'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('product.product_pricelist_item_tree_view_from_product').id, 'tree'), (False, 'form')],
            'res_model': 'product.pricelist.item',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            'context': {
                'default_product_tmpl_id': self.id,
                'default_applied_on': '1_product',
                'product_without_variants': self.product_variant_count == 1,
            },
        }

    def _compute_item_count(self):
        """
        overridden to get count of price rules set on overlay template
        """
        for template in self:
            # Pricelist item count counts the rules applicable on current template or on its variants.
            template.pricelist_item_count = template.env['product.pricelist.item'].search_count([
                '|', '|', ('product_tmpl_id', '=', template.id), ('product_id', 'in', template.product_variant_ids.ids),
                # start custom logic
                ('overlay_tmpl_id', 'in', self.overlay_template_ids.ids)])
                # end custom logic
