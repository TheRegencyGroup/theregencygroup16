from odoo import api, Command, fields, models


class OverlayProduct(models.Model):

    _name = 'overlay.product'
    _description = 'Overlay product'

    overlay_template_id = fields.Many2one('overlay.template')
    product_tmpl_id = fields.Many2one(related='overlay_template_id.product_template_id', store=True)
    name = fields.Char(related='overlay_template_id.name', store=True)
    product_id = fields.Many2one('product.product')

    @api.model
    def create(self, vals):
        res = super(OverlayProduct, self).create(vals)
        res.create_attribute_value()
        return res

    def create_attribute_value(self):
        customization_attr = self.env.ref('regency_shopsite.customization_attribute')
        pav = self.env['product.attribute.value'].create({
            'name': '%d' % self.id,
            'attribute_id': customization_attr.id,
            'sequence': 1,
        })
        ptal = self.product_tmpl_id.attribute_line_ids.filtered(lambda f: f.attribute_id == customization_attr)
        if ptal:
            ptal.write({'value_ids': [Command.link(pav.id)]})
        else:
            self.env['product.template.attribute.line'].create({
                'product_tmpl_id': self.product_tmpl_id.id,
                'attribute_id': customization_attr.id,
                'value_ids': [Command.link(pav.id)]
            })
