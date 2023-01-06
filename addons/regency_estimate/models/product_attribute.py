from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    sale_order_line_id = fields.Many2one('sale.order.line', required=False)
    estimate_product_line_id = fields.Many2one('sale.estimate.line', string="Estimate product Line", ondelete='cascade')

    _sql_constraints = [
        ('lpl_custom_value_unique', 'unique(custom_product_template_attribute_value_id, estimate_product_line_id)',
         "Only one Custom Value is allowed per Attribute Value per Lead Product Line.")
    ]


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    sequence = fields.Integer("Sequence", default=10)

    @api.constrains('active', 'value_ids', 'attribute_id')
    def _check_valid_values(self):
        res = super(ProductTemplateAttributeLine, self)._check_valid_values()
        for ptal in self:
            if ptal.product_tmpl_id.product_source_id and len(ptal.value_ids) > 1:
                raise ValidationError(
                    _("The product %s is created from the template %s and must have only one value for attribute %s") %
                    (ptal.product_tmpl_id.display_name, ptal.product_tmpl_id.product_source_id.display_name,
                     ptal.attribute_id.display_name)
                )
        return res