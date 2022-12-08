from odoo import fields, models


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    ca_product_line_id = fields.Many2one('consumption.agreement.line', string="CA product Line", ondelete='cascade')

    _sql_constraints = [
        ('lpl_custom_value_unique', 'unique(custom_product_template_attribute_value_id, ca_product_line_id)',
         "Only one Custom Value is allowed per Attribute Value per Lead Product Line.")
    ]
