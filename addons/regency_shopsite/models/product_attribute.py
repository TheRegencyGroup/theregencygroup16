from odoo import fields, models, api
from odoo.exceptions import UserError


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    _sql_constraints = [('name', 'unique(name)', 'Attribute name already exists!')]

    @api.model
    def _get_restricted_for_unlink(self):
        return (
            self.env.ref('regency_shopsite.overlay_attribute').id,
            self.env.ref('regency_shopsite.color_attribute').id,
            self.env.ref('regency_shopsite.size_attribute').id,
        )

    def unlink(self):
        if self.env['ir.config_parameter'].sudo()\
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

    def _check_overlay_attribute(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        if overlay_attribute_id.id in self.mapped('attribute_id').ids \
                and not self._context.get('from_overlay_template'):
            raise UserError('Overlay attribute line values possible to change only from overlay template')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplateAttributeLine, self).create(vals_list)
        return res

    def write(self, values):
        changed_value_ids = 'value_ids' in values
        res = super(ProductTemplateAttributeLine, self).write(values)
        return res


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _check_attribute_value_in_overlay_template(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        for rec in self:
            if not rec.product_tmpl_id.overlay_template_ids or rec.attribute_id.id == overlay_attribute_id.id:
                continue
            overlay_attribute_line_value_ids = rec.product_tmpl_id.overlay_template_ids\
                .mapped('overlay_attribute_line_ids').mapped('value_ids')
            if rec.product_attribute_value_id.id in overlay_attribute_line_value_ids.ids:
                raise UserError(f'The attribute value "{rec.product_attribute_value_id.name}" is used in one of the '
                                f'related overlay templates')

    def unlink(self):
        self._check_attribute_value_in_overlay_template()
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
        """
        Restrict values changes in the product not from the overlay template.
        """
        for ptav in self:
            if self.env.context.get('sale_multi_pricelist_product_template'):
                overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
                none_overlay_value_id = self.env.ref('regency_shopsite.none_overlay_attribute_value')
                customization_attr_id = self.env.ref('regency_shopsite.customization_attribute')
                if overlay_attribute_id == ptav.attribute_id and ptav.product_attribute_value_id != none_overlay_value_id:
                    raise UserError('Overlay attribute line values possible to change only from overlay template.')

                if customization_attr_id == ptav.attribute_id and self.env.ref(
                        'regency_shopsite.no_customization_value') != ptav.product_attribute_value_id:
                    raise UserError('Customization attribute line values possible to change only from overlay template.')
