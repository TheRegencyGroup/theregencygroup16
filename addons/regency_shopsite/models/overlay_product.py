from odoo import api, Command, fields, models


class OverlayProduct(models.Model):
    _name = 'overlay.product'
    _description = 'Overlay product'

    overlay_template_id = fields.Many2one('overlay.template')
    product_tmpl_id = fields.Many2one(string="Product template", related='overlay_template_id.product_template_id',
                                      store=True)
    name = fields.Char(related='overlay_template_id.name', store=True)
    product_id = fields.Many2one('product.product')

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        res._create_attribute_value()
        return res

    def _create_attribute_value(self):
        customization_attr = self.env.ref('regency_shopsite.customization_attribute')
        attr_value_model = self.env['product.attribute.value']
        attr_line_model = self.env['product.template.attribute.line']
        no_customization_value = self.env.ref('regency_shopsite.no_customization_value').name
        for entry in self:
            pav = attr_value_model.create({
                'name': f"{no_customization_value}: {entry.id}",
                'attribute_id': customization_attr.id,
                'sequence': 1,
            })
            ptal = entry.product_tmpl_id.attribute_line_ids.filtered(lambda f: f.attribute_id == customization_attr)
            if ptal:
                ptal.write({'value_ids': [Command.link(pav.id)]})
            else:
                attr_line_model.create({
                    'product_tmpl_id': entry.product_tmpl_id.id,
                    'attribute_id': customization_attr.id,
                    'value_ids': [Command.link(pav.id)]
                })
