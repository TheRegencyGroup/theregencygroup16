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

    def _check_image_in_overlay_template(self):
        if self.env['overlay.template'].search([('product_template_id', 'in', self.ids),
                                                ('use_product_template_image', '=', True)]):
            raise UserError('The image is used in the model "overlay.template"')

    def _compute_overlay_template_areas(self):
        overlay_template_ids = self.env['overlay.template'].search([('product_template_id', 'in', self.ids)])
        overlay_template_ids._compute_areas_json()

    def write(self, vals):
        if 'image_1920' in vals:
            self._check_image_in_overlay_template()
        prev_attribute_line_ids = self.attribute_line_ids
        res = super(ProductTemplate, self).write(vals)
        if any(x in ['image_1920', 'product_template_image_ids'] for x in vals):
            self._compute_overlay_template_areas()
        return res

    def _get_overlay_templates(self):
        self.ensure_one()
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute').id
        overlay_template_ids = self.attribute_line_ids.filtered(
            lambda x: x.attribute_id.id == overlay_attribute_id).value_ids.mapped('overlay_template_id')
        data = []
        for template_id in overlay_template_ids:
            ptav = template_id._get_product_template_attribute_value_id()
            data.append({
                'overlayAreasData': template_id.areas_json,
                'overlayAttributeValueId': ptav.id if ptav else 0,
            })
        if data:
            return Markup(json.dumps(data))
        return False

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
