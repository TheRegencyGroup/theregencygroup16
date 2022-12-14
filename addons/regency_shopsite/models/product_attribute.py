from odoo import fields, models, api
from odoo.exceptions import UserError


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    _sql_constraints = [('name', 'unique(name)', 'Attribute name already exists!')]

    @api.model
    def _get_restricted_for_unlink(self):
        return (
            self.env.ref('regency_shopsite.overlay_attribute').id,
            self.env.ref('regency_shopsite.customization_attribute').id,
            self.env.ref('regency_shopsite.color_attribute').id,
            self.env.ref('regency_shopsite.size_attribute').id,
        )

    def unlink(self):
        if self.env['ir.config_parameter'].sudo() \
                .get_param('regency_shopsite.restricted_delete_default_attributes', '1') == '1':
            if any(x in self._get_restricted_for_unlink() for x in self.ids):
                raise UserError('Attribute is default!')
        return super().unlink()


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    overlay_template_id = fields.Many2one('overlay.template', readonly=True)
    overlay_product_id = fields.Many2one('overlay.product', readonly=True)

    def _check_overlay_template_id(self):
        for rec in self:
            if rec.overlay_template_id.exists():
                raise UserError('Restricted! Attribute has overlay template!')

    def write(self, values):
        if 'overlay_template_id' in values:
            self._check_overlay_template_id()
        res = super(ProductAttributeValue, self).write(values)
        return res

    def unlink(self):
        self._check_overlay_template_id()
        return super(ProductAttributeValue, self).unlink()


class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    def _check_overlay_template_areas_image_attribute(self):
        for rec in self:
            if not rec.product_tmpl_id.overlay_template_ids:
                continue
            overlay_template_ids = rec.product_tmpl_id.overlay_template_ids \
                .filtered(lambda x: x.areas_image_attribute_id.id == rec.attribute_id.id)
            if overlay_template_ids:
                raise UserError(f'You can not remove the "{rec.attribute_id.name}" attribute because it is used in '
                                f'overlay templates with IDS({", ".join([str(x) for x in overlay_template_ids.ids])})')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplateAttributeLine, self).create(vals_list)
        return res

    def write(self, values):
        res = super(ProductTemplateAttributeLine, self).write(values)
        return res

    def unlink(self):
        self._check_overlay_template_areas_image_attribute()
        return super(ProductTemplateAttributeLine, self).unlink()


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _check_attribute_value_in_overlay_template(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        for rec in self:
            if not rec.product_tmpl_id.overlay_template_ids or rec.attribute_id.id == overlay_attribute_id.id:
                continue
            overlay_attribute_line_value_ids = rec.product_tmpl_id.overlay_template_ids \
                .mapped('overlay_attribute_line_ids').mapped('value_ids')
            if rec.product_attribute_value_id.id in overlay_attribute_line_value_ids.ids:
                raise UserError(f'The attribute value "{rec.product_attribute_value_id.name}" is used in one of the '
                                f'related overlay templates')

    def _check_overlay_template_areas_image_attribute_values(self):
        for rec in self:
            if not rec.product_tmpl_id.overlay_template_ids:
                continue
            overlay_template_ids = rec.product_tmpl_id.overlay_template_ids \
                .filtered(lambda x: x.areas_image_attribute_id.id == rec.attribute_id.id and
                                    rec.product_attribute_value_id.id in x.areas_image_attribute_selected_value_ids.ids)
            if overlay_template_ids:
                raise UserError(f'You can not remove "{rec.product_attribute_value_id.name}" value because it is used '
                                f'in overlay templates with IDS({", ".join([str(x) for x in overlay_template_ids.ids])})')

    def unlink(self):
        self._check_attribute_value_in_overlay_template()
        self._check_overlay_template_areas_image_attribute_values()
        return super(ProductTemplateAttributeValue, self).unlink()

    def _get_combination_name(self):
        """Exclude values from single value lines or from no_variant attributes."""
        ptavs = self._without_no_variant_attributes().with_prefetch(self._prefetch_ids)
        ptavs = ptavs._filter_single_value_lines().with_prefetch(self._prefetch_ids)
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        customize_attribute_id = self.env.ref('regency_shopsite.customization_attribute')
        ptav_name_list = []
        for ptav in ptavs:
            if ptav.attribute_id.id == overlay_attribute_id.id and ptav.product_attribute_value_id.overlay_template_id:
                name = ptav.product_attribute_value_id.overlay_template_id.name
            elif ptav.attribute_id.id == customize_attribute_id.id and ptav.product_attribute_value_id.overlay_product_id:
                name = ptav.product_attribute_value_id.overlay_product_id.name
            else:
                name = ptav.name
            ptav_name_list.append(name)
        return ", ".join(ptav_name_list)

    @api.constrains('product_attribute_value_id', 'ptav_active')
    def _check_correct_attribute_value(self):
        for ptav in self:
            overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
            customization_attribute_id = self.env.ref('regency_shopsite.customization_attribute')
            none_customization_attribute_value_id = self.env.ref('regency_shopsite.none_overlay_attribute_value')

            if ptav.attribute_id.id == overlay_attribute_id.id and \
                    not self.env.context.get('from_overlay_template', False):
                raise UserError('Overlay attribute line values possible to change only from overlay template.')
            elif ptav.attribute_id.id == customization_attribute_id.id and \
                    not self.env.context.get('from_overlay_product', False) and \
                    ptav.product_attribute_value_id.id != none_customization_attribute_value_id.id:
                raise UserError('Customization attribute line values possible to change only from customization.')
