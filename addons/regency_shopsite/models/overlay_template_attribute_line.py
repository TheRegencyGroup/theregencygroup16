from odoo import fields, models, api


class OverlayTemplateAttributeLine(models.Model):
    _name = 'overlay.template.attribute.line'
    _description = "Overlay template attribute line"
    _rec_name = 'attribute_id'

    overlay_tmpl_id = fields.Many2one('overlay.template', string="Overlay Template", ondelete='cascade', required=True)
    product_tmpl_id = fields.Many2one('product.template', related='overlay_tmpl_id.product_template_id')
    attribute_id = fields.Many2one('product.attribute', string="Attribute", ondelete='cascade', required=True,
                                   domain="[('id', 'in', possible_attribute_ids)]")
    value_ids = fields.Many2many('product.attribute.value', string="Values", required=True,
                                 domain="[('id', 'in', possible_value_ids)]")
    possible_attribute_ids = fields.Many2many('product.attribute', compute='_compute_possible_attribute_ids')
    possible_value_ids = fields.Many2many('product.attribute.value', compute='_compute_possible_value_ids')

    @api.depends('product_tmpl_id.attribute_line_ids.attribute_id',
                 'overlay_tmpl_id.overlay_attribute_line_ids.attribute_id')
    def _compute_possible_attribute_ids(self):
        for overlay in self:
            product_attributes = overlay.product_tmpl_id.attribute_line_ids.attribute_id
            selected_attributes = overlay.overlay_tmpl_id.overlay_attribute_line_ids.attribute_id
            overlay_attribute = self.env.ref('regency_shopsite.overlay_attribute')
            possible_attributes = product_attributes - selected_attributes - overlay_attribute
            overlay.possible_attribute_ids = [fields.Command.set(possible_attributes.ids)]

    @api.depends('product_tmpl_id.attribute_line_ids.value_ids',
                 'attribute_id')
    def _compute_possible_value_ids(self):
        for overlay in self:
            possible_values_ids = overlay.product_tmpl_id.attribute_line_ids.filtered(
                lambda attribute_line: attribute_line.attribute_id == overlay.attribute_id).value_ids
            overlay.possible_value_ids = [fields.Command.set(possible_values_ids.ids)]
