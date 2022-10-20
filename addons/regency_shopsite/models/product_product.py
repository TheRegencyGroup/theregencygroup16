from odoo import api, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('attribute_line_ids')
    def _onchange_attribute_line(self):
        overlay_attr = self.env.ref('regency_shopsite.overlay_attribute')
        customization_attr = self.env.ref('regency_shopsite.customization_attribute')

        if {overlay_attr.id, customization_attr.id}.intersection(set(self.attribute_line_ids.ids)):
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Cannot add Overlay/Customization attribute manually.'),
                }
            }
